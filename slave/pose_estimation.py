# print("원점:", corner)
# print("x좌표: \n", imgpts[0])
# print("y좌표: \n", imgpts[1])
# print("z좌표: ", imgpts[2])
# project 3D points to image plane

import cv2
import numpy as np
import simple_camera
import signal
row=9
col=6
signal.GPIO_setup()
def draw(img, corners, imgpts):
    corner = tuple(corners[0].ravel())
    img = cv2.line(img, corner, tuple(imgpts[0].ravel()), (255,0,0), 5)
    img = cv2.line(img, corner, tuple(imgpts[1].ravel()), (0,255,0), 5)
    img = cv2.line(img, corner, tuple(imgpts[2].ravel()), (0,0,255), 5)
    return img

capture = cv2.VideoCapture(simple_camera.gstreamer_pipeline(flip_method=0), cv2.CAP_GSTREAMER)
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
objp = np.zeros((row * col, 3), np.float32)
objp[:, :2] = np.mgrid[0:row, 0:col].T.reshape(-1, 2)
objpoints = []
imgpoints = []


mtx=np.array([[639.13004417, 0, 325.40873715],
              [0, 852.38716718, 251.51136554],
              [0, 0, 1]])
dist=np.array([7.81831431e-02, 6.76798173e-01, 1.93216601e-03, 1.10072242e-03, -2.76646271e+00])
axis = np.float32([[3, 0, 0], [0, 3, 0], [0, 0, -3]]).reshape(-1, 3)
while True:
    apple, img = capture.read()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, corners = cv2.findChessboardCorners(gray, (row, col), None)
    if ret == True:
        corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)

        # Find the rotation and translation vectors.
        _, rvecs, tvecs, inliers = cv2.solvePnPRansac(objp, corners2, mtx, dist)
        imgpts, jac = cv2.projectPoints(axis, rvecs, tvecs, mtx, dist)

        img = draw(img, corners2, imgpts)

        corners2_mod = tuple(corners2[0].ravel())
        steer_val = (corners2_mod[0] - imgpts[2][0][0])
        print(steer_val)
        if steer_val<-30:
            # signal.Right()
            print("좌회전")
        elif steer_val>10:
            # signal.Left()
            print("우회전")
        else:
            # signal.Forward()
            print("직진")
        cv2.imshow('img', img)
        if cv2.waitKey(1) > 0: break
    else:
        cv2.imshow('img', img)
        if cv2.waitKey(1) > 0: break
capture.release()
cv2.destroyAllWindows()
