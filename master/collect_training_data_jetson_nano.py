__author__ = 'zhengwang'

import numpy as np
import cv2
#import serial
import pygame
from pygame.locals import *
import socket
import time
import os
import Device

import signal
from signal import GPIO_setup

class CollectTrainingData(object):
    
    def __init__(self, host, port, input_size):

        # 소켓이란 네트워크를 통하는 컴퓨터의 외부와 컴퓨터 내부의 프로그램을 이어주는 인터페이스
        # 소켓을 생성(패밀리. 소켓), (AF_INET, SOCK_STREAM은 가장 많이 쓰임)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # 서버가 특정 포트를 열고 입력을 기다리기 위해서는 소켓을 포트에 바인드 하는 과정이 선행되어야함
        # bind로 넘기는 인자는 튜플로 감싸서 전달
        self.server_socket.bind((host, port))
        # 클라이언트가 해당 포트에 접속하는 것을 기다림
        # 접속시도를 알아챘다면 서버에서도 그 요청을 받아서 접속을 시작함
        self.server_socket.listen(1)

        # accept a single connection
        #self.connection = self.server_socket.accept()[0].makefile('rb')

        # 서버는 최초 생성되어 듣는 소켓이 아닌 accept()의 리턴으로 제공되는 소켓을
        # 사용하여 클라이언트와 정보를 주고 받을 수 있다.
        self.connection = self.server_socket.accept()[0]
        self.send_inst = True

        self.input_size = input_size

        # create labels
        self.k = np.zeros((4, 4), 'float')
        for i in range(4):
            self.k[i, i] = 1

        pygame.init()
        pygame.display.set_mode((250, 250))
        pygame.key.set_repeat(True)

    def collect(self):

        saved_frame = 0
        total_frame = 0

        # collect images for training
        print("Start collecting images...")
        print("Press 'q' or 'x' to finish...")
        start = cv2.getTickCount() # os 부팅 후 지나간 시간을 msec단위로 반환

        X = np.empty((0, self.input_size))
        y = np.empty((0, 4))

        # stream video frames one by one
        try:
            # 바이트 선언
            stream_bytes = b' '
            frame = 1
            cnt = 0
            while self.send_inst:
                #stream_bytes += self.connection.read(1024)
                # recv()함수를 통해서 소켓으로부터 데이터를 읽음
                stream_bytes += self.connection.recv(1024) # 왜 1024?
                first = stream_bytes.find(b'\xff\xd8')
                last = stream_bytes.find(b'\xff\xd9')

                if first != -1 and last != -1:
                    jpg = stream_bytes[first:last + 2]
                    stream_bytes = stream_bytes[last + 2:]

                    image = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_GRAYSCALE)
                    
                    # select lower half of the image
                    height, width = image.shape
                    #roi = image[int(height/2):height, :]
                    roi = image[120:240, :]

                    cv2.imshow('roi', roi)
                    cv2.imshow('origin', image)

                    # reshape the roi image into a vector
                    temp_array = roi.reshape(1, int(height/2) * width).astype(np.float32)
                    

                    frame += 1
                    total_frame += 1

                    # get input from human driver
                    gamepad = InputDevice('/dev/input/event4')
                    GPIO_setup()
                    for event in gamepad.read_loop(): #User did something
                        if event.type == ecodes.EV_ABS:
                            absevent = categorize(event)

                            # simple orders
                            if (absevent.event.value == -1 and absevent.event.code == 17):
                                print("Forward")
                                saved_frame += 1
                                X = np.vstack((X, temp_array))
                                y = np.vstack((y, self.k[2]))
                                self.connection.send('w'.encode())

                            elif (absevent.event.value == 1 and absevent.event.code == 17):
                                print("Reverse")
                                saved_frame += 1
                                self.connection.send('x'.encode())
                                #X = np.vstack((X, temp_array))
                                #y = np.vstack((y, self.k[3]))

                            elif (absevent.event.value == -1 and absevent.event.code == 16):
                                print("Right")
                                X = np.vstack((X, temp_array))
                                y = np.vstack((y, self.k[1]))
                                saved_frame += 1
                                self.connection.send('d'.encode())

                            elif (absevent.event.value == 1 and absevent.event.code == 16):
                                print("Left")
                                X = np.vstack((X, temp_array))
                                y = np.vstack((y, self.k[0]))
                                saved_frame += 1
                                self.connection.send('a'.encode())

                            #elif key_input[pygame.K_q]:
#                                 print("exit")
#                                 self.send_inst = False
#                                 self.connection.send('q'.encode())
#                                 self.connection.close()
#                                 break

#                             #elif key_input[pygame.K_s]:
#                                 print("stop")
#                                 self.connection.send('s'.encode())

#                             #elif key_input[pygame.K_f]:
#                                 print("reset")
#                                 X = np.empty((0, self.input_size))
#                                 y = np.empty((0, 4))

                        else : # key up
                            self.connection.send('s'.encode())

                    if cv2.waitKey(3): # 유니코드 문자-> 해당문자의 코드 포인트정
                        break

            # save data as a numpy file
            file_name = str(int(time.time()))
            directory = "training_data"
            if not os.path.exists(directory):
                os.makedirs(directory)
            try:
                np.savez(directory + '/' + file_name + '.npz', train=X, train_labels=y)
            except IOError as e:
                print(e)

            end = cv2.getTickCount()
            # calculate streaming duration
            print("Streaming duration: , %.2fs" % ((end - start) / cv2.getTickFrequency()))

            print(X.shape)
            print(y.shape)
            print("Total frame: ", total_frame)
            print("Saved frame: ", saved_frame)
            print("Dropped frame: ", total_frame - saved_frame)

        finally:
            self.connection.close()
            self.server_socket.close()


if __name__ == '__main__':
    # host, port
    h, p = "192.168.0.90", 5034

    # serial port
    #sp = "/dev/tty.usbmodem1421"

    # vector size, half of the image
    s = 120 * 320

    ctd = CollectTrainingData(h, p, s)
    ctd.collect()
