import numpy as np
import cv2
import cv2.aruco as aruco
import simple_camera
import statistics
import Ultrasonic
import time
import inspect
import smbus
import socket
import math
import threading

import matplotlib.pyplot as plt
import multiprocessing

class jetson_follower:


    def __init__(self):
        self.host = '192.168.0.3'
        self.port = 1234
        self.port_image = 1235

        self.mtx = np.array([[293.72378683, 0, 313.70240717],
                        [0, 391.86971237, 236.24858293],
                        [0, 0, 1]])
        self.dist = np.array([-0.27801493, 0.10637265, -0.00062831, -0.00040659, -0.02419783])

        self.follow_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.follow_socket.connect((self.host, self.port))
        self.image_follow = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.image_follow.connect((self.host, self.port_image))



        self.dev = smbus.SMBus(1)


    def recvall(self,sock,count):
        buf = b''
        while count:
            newbuf = sock.recv(count)
            if not newbuf: return None
            buf += newbuf
            count -= len(newbuf)
        return buf

    def connect(self):
        pass
       # self.follow_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
       # self.follow_socket.connect((self.host,self.port))
        # while 1:
        #     if flag == 1:
        #         self.follow_socket.send('y'.encode('utf-8'))
        #         break
        #     else:
        #         self.follow_socket.send('n'.encode('utf-8'))
        #         break

    def show(self):

        while 1:

            length = self.recvall(self.image_follow, 16)
            stringData = self.recvall(self.image_follow, int(length))
            data = np.frombuffer(stringData, dtype='uint8')
            decimg = cv2.imdecode(data, cv2.IMREAD_COLOR)  # GRAY_SCALE -> 채널 1
            decimg = cv2.resize(decimg, (320, 240))
           # cv2.imshow('Client', decimg)
           # if cv2.waitKey(1) & 0xFF == ord('q'):
           #      break
       # cv2.destroyAllWindows()

    ###------------------ ARUCO TRACKER ---------------------------
    def ARUCO_TRACKER(self):
        print('run aruco')
        count = 0

        cap = cv2.VideoCapture(simple_camera.gstreamer_pipeline(flip_method=0), cv2.CAP_GSTREAMER)
        ls = []
        while (cap.isOpened()):


            ls.append(Ultrasonic.distance())
            if len(ls) > 10:  ## 중간값 필터로 10개중에 한개 받기!
                del ls[0]
        # print(statistics.median(ls))
            med_ultra=statistics.median(ls)
            print(med_ultra)
            ret, frame = cap.read()

        # operations on the frame

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # set dictionary size depending on the aruco marker selected
            aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_50)

        # detector parameters can be set here (List of detection parameters[3])
            parameters = aruco.DetectorParameters_create()
            parameters.adaptiveThreshConstant = 10

        # lists of ids and the corners belonging to each id
            corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)

        # font for displaying text (below)
            font = cv2.FONT_HERSHEY_SIMPLEX

        # check if the ids list is not empty
        # if no check is added the code will crash
            if med_ultra > 19:
                if np.all(ids != None):
                    if [1] in ids:

                        ids = ids.tolist()

                        result = [element1 for element2 in ids for element1 in element2]
                        ids = np.array(ids)

                        ids_index = result.index(1)
                        corners = [corners[ids_index]]
                    else:
                        corners = [corners[0]]
                # and(med_ultra < 80 ):
                # estimate pose of each marker and return the values
                # rvet and tvec-different from camera coefficients
                    rvec, tvec ,_ = aruco.estimatePoseSingleMarkers(corners, 0.05, self.mtx, self.dist)
                #(rvec-tvec).any() # get rid of that nasty numpy value array error

                    #for i in range(0, ids.size):
                    # draw axis for the aruco markersqqqq
                    #aruco.drawAxis(frame, self.mtx, self.dist, rvec[i] , tvec[i], 0.01)

                    x = (corners[0][0][0][0] + corners[0][0][1][0] + corners[0][0][2][0] + corners[0][0][3][0]) / 4
                    y = (corners[0][0][0][1] + corners[0][0][1][1] + corners[0][0][2][1] + corners[0][0][3][1]) / 4


                    self.follow_socket.send('y'.encode('utf-8'))

                    if (x <300):#280
                        print("왼쪽")
                        self.dev.write_i2c_block_data(0x04, 0, [0])
                    elif (x>340):#350
                        print("오른쪽")
                        self.dev.write_i2c_block_data(0x04, 0, [1])

                    else:
                        print("직진")
                        self.dev.write_i2c_block_data(0x04, 0, [2])


                    aruco.drawDetectedMarkers(frame, corners)

                    # code to show ids of the marker found
                    #strg = ''
                    #for i in range(0, ids.size):
                    #    strg += str(ids[i][0])+', '

                    #cv2.putText(frame, "Id: " + strg, (0,64), font, 1, (0,255,0),2,cv2.LINE_AA)
                else:
                    # code to show 'No Ids' when no markers are found
                    cv2.putText(frame, "No Ids", (0,64), font, 1, (0,255,0),2,cv2.LINE_AA)

                    print("인식불가, 마스터에게 정지신호 송출 및 적외선센서 실행")
                    self.follow_socket.send('n'.encode('utf-8'))
                    self.dev.write_i2c_block_data(0x04, 0, [10])

            elif med_ultra>100  or med_ultra<=19:
                # code to show 'No Ids' when no markers are found
                cv2.putText(frame, "No Ids", (0, 64), font, 1, (0, 255, 0), 2, cv2.LINE_AA)
                print("차량근접, 슬레이브 정지")
                self.dev.write_i2c_block_data(0x04, 0, [4])


            # display the resulting frame
            cv2.imshow('frame',frame)

            # cv2.imwrite("images/frame%d.jpg" % count, frame)
            # count+=1

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cap.release()
        cv2.destroyAllWindows()

    # if follow_socket.recv(1).decode('utf-8') == 's':
    #     follow_socket.close()
    #     break

# When everything done, release the capture



if __name__ == "__main__":
    jetson = jetson_follower()

    auto =  threading.Thread(target=jetson.ARUCO_TRACKER)
    show = threading.Thread(target=jetson.show)

    auto.start()
    show.start()

    auto.join()
    show.join()
