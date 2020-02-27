import Jetson.GPIO as gpio
import time
import statistics
import math

def distance(measure='cm'):
    det1=False
    det2=False
    try:
        gpio.setmode(gpio.BOARD)
        gpio.setup(11, gpio.OUT)
        gpio.setup(13, gpio.IN)

        gpio.output(11, gpio.HIGH)
        time.sleep(0.00001)
        gpio.output(11, gpio.LOW)


        while gpio.input(13) == False:

            if det1==False:
                t1 = time.time()
                det1=True
            nosig =time.time()
            if((nosig-t1)>0.01):
                print("반복문 탈출.")
                break
        while gpio.input(13) == True:
            if ~det2:
                t2=time.time()
                det2=True
            sig = time.time()

        tl = sig - nosig

        if measure == 'cm':
            distance = round((tl / 0.000058),2)
        else:
            print('improper choice of measurement: cm')
            distance = None
        # gpio.cleanup()
        # print("거리: {0}".format(distance))
        return distance
    except:
        distance = math.inf
        # gpio.cleanup()
        # print("거리: {0}".format(distance))
        return distance


if __name__ == "__main__":
    ls = []
    while 1:
        ls.append(distance())
        if len(ls)>10: ## 중간값 필터로 10개중에 한개 받기!
            del ls[0]
        # print(statistics.median(ls))
        print("Distance: {0}cm".format(statistics.median(ls)))

