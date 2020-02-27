import smbus
from evdev import InputDevice,ecodes,categorize
import socket

dev=smbus.SMBus(1)
gamepad = InputDevice('/dev/input/event5')

# host = '192.168.0.48'
# port = 1234
# leader_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# leader_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# leader_socket.bind((host, port))
# leader_socket.listen(1)
#
# follow, addr = leader_socket.accept()
#
#
# while 1:
#     signal = follow.recv(1).decode('utf-8')
#     print('신호:')
#     print(signal)

for event in gamepad.read_loop():

    if event.type == ecodes.EV_ABS:
        absevent = categorize(event)
        if (absevent.event.value == -1 and absevent.event.code == 16):
            dev.write_i2c_block_data(0x04, 0, [0])
        elif (absevent.event.value == 1 and absevent.event.code == 16):
            dev.write_i2c_block_data(0x04, 0, [1])
        elif (absevent.event.value == -1 and absevent.event.code == 17):
            dev.write_i2c_block_data(0x04, 0, [2])
        elif (absevent.event.value == 1 and absevent.event.code == 17):
            dev.write_i2c_block_data(0x04, 0, [4])
        else :
            dev.write_i2c_block_data(0x04,0,[3])
