# from evdev import InputDevice,categorize,ecodes
# from select import select
# gamepad = InputDevice('/dev/input/event4')
# for event in gamepad.read_loop():
#     keyevent=categorize(event)
#     print(keyevent.event)
#

from evdev import InputDevice,ecodes,categorize

gamepad = InputDevice('/dev/input/event7')

for event in gamepad.read_loop():
    if event.type == ecodes.EV_ABS:
        absevent = categorize(event)
        if(absevent.event.value==-1 and absevent.event.code==16):
            print('Left')
        elif(absevent.event.value == 1 and absevent.event.code == 16):
            print('Right')
        elif(absevent.event.value == -1 and absevent.event.code == 17):
            print('Up')
        elif(absevent.event.value == 1 and absevent.event.code == 17):
            print('Down')
