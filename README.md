# 포스코아카데미 8기 A반 4조 AI 프로젝트
  딥러닝 모델 기반 자율주행 + 3d 마커 인식 활용한 군집 주행
  
# 개발환경
* Nvidia Jetson Nano
* Adduino
* Python3
* Tensorflow 1.13.1
* OpenCV 4.1.1
* CUDA 9.0

# 실행방법

1. Master 폴더의 **jetson_main_class.py** 실행
2. 커맨드 창에서 1 입력 시 마스터 차량 자율주행, q 입력시 정지
3. Slave 폴더의 **Aruco_traker.py** 실행
3. 커맨드 창에서 2 입력 시 슬레이브 차량과 군집주행
