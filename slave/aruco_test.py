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

# # client
# host = '192.168.0.4'
# port = 1234
# follow_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# follow_socket.connect((host,port))

#
dev=smbus.SMBus(1)
count=0

cap = cv2.VideoCapture(simple_camera.gstreamer_pipeline(flip_method=0), cv2.CAP_GSTREAMER)

# 기본 카메라
# mtx=np.array([[639.13004417, 0, 325.40873715],
#               [0, 852.38716718, 251.51136554],
#               [0, 0, 1]])
# dist=np.array([7.81831431e-02, 6.76798173e-01, 1.93216601e-03, 1.10072242e-03, -2.76646271e+00])

#광각 카메라(강의실)
mtx=np.array([[293.72378683, 0, 313.70240717],
              [0, 391.86971237, 236.24858293],
              [0, 0, 1]])
dist=np.array([-0.27801493, 0.10637265, -0.00062831, -0.00040659, -0.02419783])

# 광각 카메라(4층의 창고)
# mtx=np.array([[9.28856934e+02, 0, 2.94132480e+02],
#  [  0, 1.13143391e+03, 3.04901262e+02],
#  [  0, 0, 1]])
# dist=np.array([-1.6930846,  7.63837108, -0.06943976, -0.03426694, -25.75795386])


ls = []
###------------------ ARUCO TRACKER ---------------------------
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
    if med_ultra > 9:
        if np.all(ids != None):

            if [1] in ids:
                ids = np.delete(ids, np.where(ids == [0]))
                ids = np.delete(ids, np.where(ids == [2]))
                ids = np.array([ids])
            # estimate pose of each marker and return the values
            # rvet and tvec-different from camera coefficients
            rvec, tvec ,_ = aruco.estimatePoseSingleMarkers(corners, 0.05, mtx, dist)
            #(rvec-tvec).any() # get rid of that nasty numpy value array error

            for i in range(0, ids.size):
                # draw axis for the aruco markersqqqq
                aruco.drawAxis(frame, mtx, dist, rvec[i] , tvec[i], 0.01)

            x = (corners[0][0][0][0] + corners[0][0][1][0] + corners[0][0][2][0] + corners[0][0][3][0]) / 4
            y = (corners[0][0][0][1] + corners[0][0][1][1] + corners[0][0][2][1] + corners[0][0][3][1]) / 4


            # follow_socket.send('y'.encode('utf-8'))
            if (x <300):#280
                print("왼쪽")
                # dev.write_i2c_block_data(0x04, 0, [0])
            elif (x>340):#350
                print("오른쪽")
                # dev.write_i2c_block_data(0x04, 0, [1])
            else:
                print("직진")
                # dev.write_i2c_block_data(0x04, 0, [2])


            # if (rvec[0][0][0] > 0  and  rvec[0][0][2]>=0.3) or (x <280):
            #     print("왼쪽")
            #     dev.write_i2c_block_data(0x04, 0, [0])
            # elif (rvec[0][0][0] < 0  and  rvec[0][0][2]>=0.3) or (x>350):
            #     print("오른쪽")
            #     dev.write_i2c_block_data(0x04, 0, [1])
            # else:
            #     print("직진")
            #     dev.write_i2c_block_data(0x04, 0, [2])
            # draw a square around the markers
            aruco.drawDetectedMarkers(frame, corners)

            # code to show ids of the marker found
            strg = ''
            for i in range(0, ids.size):
                strg += str(ids[i][0])+', '

            cv2.putText(frame, "Id: " + strg, (0,64), font, 1, (0,255,0),2,cv2.LINE_AA)
        else:
            # code to show 'No Ids' when no markers are found
            cv2.putText(frame, "No Ids", (0,64), font, 1, (0,255,0),2,cv2.LINE_AA)

            print("인식불가, 마스터에게 정지신호 송출")
            # follow_socket.send('n'.encode('utf-8'))
            # dev.write_i2c_block_data(0x04, 0, [2])
    elif med_ultra == math.inf or med_ultra <= 9:
        # code to show 'No Ids' when no markers are found
        cv2.putText(frame, "No Ids", (0, 64), font, 1, (0, 255, 0), 2, cv2.LINE_AA)
        # print("차량근접, 슬레이브 정지")
        # dev.write_i2c_block_data(0x04, 0, [4])

    # display the resulting frame
    cv2.imshow('frame',frame)
    # cv2.imwrite("images/frame%d.jpg" % count, frame)
    count+=1
    if cv2.waitKey(1) & 0xFF == ord('q'):
        # follow_socket.close()
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
