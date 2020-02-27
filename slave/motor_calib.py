
IN1 = 31
IN2 = 33
IN3 = 35
IN4 = 37

import sys
sys.path.append('/opt/nvidia/jetson-gpio/lib/python')
sys.path.append('/opt/nvidia/jetson-gpio/lib/python/Jetson/GPIO')
sys.path.append('/home/nvidia/repositories/nano_gpio/gpio_env/lib/python2.7/site-packages/periphery/')
import time
import Jetson.GPIO as GPIO
import Device
from evdev import InputDevice,ecodes,categorize
import Ultrasonic
import math
###########PCA9685 setting################
# discover I2C devices

i2c_devs = Device.Device.get_i2c_bus_numbers()
i2c_num=1

pca9685 = Device.Device(0x40, i2c_num)

# Set duty cycle
pca9685.set_pwm(0, 1000)
pca9685.set_pwm(1, 1000)
# set pwm freq
pca9685.set_pwm_frequency(500)
def set_duty_cycle(pwmdev, channel, dt):
    """
    @pwmdev a Device class object already configured
    @channel Channel or PIN number in PCA9685 to configure 0-15
    @dt desired duty cycle
    """
    val = (dt*4095)//100
    pwmdev.set_pwm(channel,val)

#GPIO setup
def GPIO_setup():
    GPIO.setmode(GPIO.BOARD)
    mode = GPIO.getmode()
    GPIO.setup(IN1, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(IN2, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(IN3, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(IN4, GPIO.OUT, initial=GPIO.LOW)
# Stop
def Stop():
    set_duty_cycle(pca9685, 0, 0)
    set_duty_cycle(pca9685, 1, 0)
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.LOW)
    # time.sleep(0.3)

# Forward
def Forward():
    set_duty_cycle(pca9685, 0, 20)
    set_duty_cycle(pca9685, 1, 21)
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)
    # time.sleep(0.3)
# Backward
def Backward():
    set_duty_cycle(pca9685, 0, 20)
    set_duty_cycle(pca9685, 1, 20)
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)
    # time.sleep(0.3)
# Left
def Left():
    set_duty_cycle(pca9685, 0, 15)
    set_duty_cycle(pca9685, 1, 30)
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)
    # time.sleep(0.3)
# Left
def Right():
    set_duty_cycle(pca9685, 0, 30)
    set_duty_cycle(pca9685, 1, 15)
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)
    # time.sleep(0.3)

if __name__ == '__main__':
    GPIO_setup()
    Backward()
    time.sleep(1)
    Stop()