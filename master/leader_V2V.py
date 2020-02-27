# -*- coding: utf-8 -*-
import numpy as np
import cv2
import threading
# import  model_tmp
from model_tmp import NeuralNetwork
import socket
import serial
import smbus
import multiprocessing
import time

# jetsonnano 카메라 설정
def gstreamer_pipeline(
    capture_width=320,
    capture_height=240,
    display_width=320,
    display_height=240,
    framerate=30,
    flip_method=0,
):
    return (
        "nvarguscamerasrc ! "
        "video/x-raw(memory:NVMM), "
        "width=(int)%d, height=(int)%d, "
        "format=(string)NV12, framerate=(fraction)%d/1 ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
        "videoconvert ! "
        "video/x-raw, format=(string)BGR ! appsink"
        % (
            capture_width,
            capture_height,
            framerate,
            flip_method,
            display_width,
            display_height,
        )
    )

# 자율주행 클래스
class Leader(object):
    def __init__(self):
        self.host = '192.168.0.3'
        self.port = 1234
        self.image_port = 1235 # 프레임 follow 차량에 전송용 소켓
        self.dev = smbus.SMBus(1)
        self.follow = None #follow ip
        self.data = None # line 예측값
        self.platoon = False
        self.leader_socket = None
        self.image_socket = None
        self.image_follow = None

    def CONNECT(self):
        print('START CONNECT')
        self.leader_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.leader_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.leader_socket.bind((self.host, self.port))
        self.leader_socket.listen(1)
        self.follow, self.addr = self.leader_socket.accept()
        print('connect ok')
        print(self.addr)


    def SHOW(self):
        print('START FRAME CONNECT')
        #
        self.image_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.image_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.image_socket.bind((self.host,self.image_port))
        self.image_socket.listen(1)
        self.image_follow, self.addr2 = self.image_socket.accept()
        print('connect show')
        print(self.addr2)

        self.dev.write_i2c_block_data(0x04, 0, [3])

        self.platoon = True


    def MOTOR_P(self,data):

        while True:
            self.signal = self.follow.recv(1).decode('utf-8')

            print('run motor_p')
            # time.sleep(0.1)
            if self.signal == 'y':
                print('수신 =======')
                if data == 0:
                    print('LEFT')
                    self.dev.write_i2c_block_data(0x04, 0, [0])
                    break
                elif data == 1:
                    print('RIGHT')
                    self.dev.write_i2c_block_data(0x04, 0, [1])
                    break
                elif data == 2:
                    print('FOWARD')
                    self.dev.write_i2c_block_data(0x04, 0, [2])
                    break
                # else:
                #     pass

            elif self.signal == 'n':
                print('STOP')
                self.dev.write_i2c_block_data(0x04, 0, [3])
                break

            else:
                self.dev.write_i2c_block_data(0x04, 0, [3])
                break


    #아두이노로 모터 제어
    def MOTOR(self,data):
        while True:
            if data == 0:
                print('LEFT')
                self.dev.write_i2c_block_data(0x04, 0, [0])
                break
            elif data == 1:
                print('RIGHT')
                self.dev.write_i2c_block_data(0x04, 0, [1])
                break
            elif data == 2:
                print('FOWARD')
                self.dev.write_i2c_block_data(0x04, 0, [2])
                break

    def RUN(self):
        # 모델 생성 + 카메라 실행

        model = NeuralNetwork()
        model.load_model(path='model_data/posla_model_old_new.h5')

        print("Start video stream")
        cap = cv2.VideoCapture(gstreamer_pipeline(flip_method=0), cv2.CAP_GSTREAMER)
        #time.sleep(10)
        #count = 0
        while True:
            # 그레이 스케일 변환으로 채널 제거 + 이미지 크기 변환
            ret, frame = cap.read()
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            tmp = cv2.imencode('.jpg', frame)[1]
            data = np.array(tmp)
            stringData = data.tostring()

            try:

                if ret:
                    img = cv2.resize(img,(320,240))
                    roi = img[120:240, :]
                    image_array = np.reshape(roi, (-1, 120, 320, 1))
                    cv2.imshow('roi', roi)

                    # 프레임을 모델에 입력해서 라인 예측
                    self.data = model.predict(image_array)

                    # 모터 실행1
                    if self.platoon ==True:
                        self.MOTOR_P(self.data)
                        self.image_follow.sendall(str(len(stringData)).encode().ljust(16) + stringData)
                    else:
                        self.MOTOR(self.data)

            except:
                pass
            # q를 누르면 종료
            if cv2.waitKey(1) & 0xFF == ord('q'):
                cap.release()
                self.dev.write_i2c_block_data(0x04, 0, [3])

                if self.platoon == True:
                    #self.follow.send('s'.encode('utf-8'))
                    self.leader_socket.close
                    self.image_socket.close
                    self.follow.close
                    self.image_follow.close

                break


if __name__ == '__main__':

    while 1:

        jetson_leader = Leader()# leader 차 클래스 생성

        print('1: Run 2: platooning 3: stop\n')

        cmd = int(input('command:'))

        if cmd == 1:
            #jetson.RUN()
            print('Run')
            run = threading.Thread(target=jetson_leader.RUN)
            run.start()
            run.join()

        elif cmd == 2:
            print('platoon')

            #pr1 = multiprocessing.Process(target=jetson_leader.RUN)
            # jetson_leader.CONNECT()
            # #pr2 = multiprocessing.Process(target=jetson_leader.CONNECT)
            # pr1.start()
            # jetson_leader.CONNECT()
            # #pr2.start()
            # pr1.join()
            # #pr2.join()

            # run = multiprocessing.Process(target=jetson_leader.RUN)
            # connect = multiprocessing.Process(target=jetson_leader.CONNECT)
            # show = multiprocessing.Process(target=jetson_leader.SHOW)
            # run.start()
            # connect.start()
            # show.start()
            #
            # run.join()
            # connect.join()
            # show.join()



            run = threading.Thread(target=jetson_leader.RUN)
            connect = threading.Thread(target=jetson_leader.CONNECT)
            show = threading.Thread(target=jetson_leader.SHOW)
            run.start()
            connect.start()
            show.start()

            run.join()
            connect.join()
            show.join()
        elif cmd == 3:
            print('stop')
            break
        else:
            print('input correct command:')
