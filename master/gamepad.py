# from evdev import InputDevice,categorize,ecodes
# from select import select
# gamepad = InputDevice('/dev/input/event4')
# for event in gamepad.read_loop():
#     keyevent=categorize(event)
#     print(keyevent.event)
#

from evdev import InputDevice, categorize, ecodes, KeyEvent

gamepad = InputDevice('/dev/input/event4')

for event in gamepad.read_loop():
    if event.type == ecodes.EV_ABS:
        absevent = categorize(event)
        print(absevent.event.value,absevent.event.code)
        # print(type(absevent.event.value))
        #print(absevent.event.value[1],absevent.event.code[1])


#
#
#
#         if(absevent.event.value==-1 and absevent.event.code==16):
#            print('Left')
#         elif(absevent.event.value == 1 and absevent.event.code == 16):
#            print('Right')
#         elif(absevent.event.value == -1 and absevent.event.code == 17):
#            print('Up')
#         elif(absevent.event.value == 1 and absevent.event.code == 17):
#            print('Down')
#         elif (absevent.event.value == 32767 and absevent.event.code == 1):
#             print('exit')
#
# for event in gamepad.read_loop():
#     if event.type == ecodes.EV_KEY:
#         keyevent = categorize(event)
#         # print(keyevent)
#         if keyevent.keystate== KeyEvent.key_down:
#             if (keyevent.keycode[0]=='BTN_A'):
#                 print('Down')
#             elif (keyevent.keycode[0] =='BTN_WEST'):
#                 print('Up')
#             elif (keyevent.keycode[0] == 'BTN_NORTH'):
#                 print('Left')
#             elif (keyevent.keycode[0] == 'BTN_B'):
#                 print('Right')
#             elif (keyevent.keycode == 'BTN_THUMBR'):
#                 print('exit')


