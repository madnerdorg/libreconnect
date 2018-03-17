from pyfirmata import Arduino, util
try:
    board = Arduino('COM12')
except:
    print("Failed (bad port)")

if board.firmware == None:
    print("Failed (not firmata)")
print(board.firmware)
# command = "board" + ".digital[13].write(1)"
# eval(command)

