
try:
    import board 
    import digitalio                   
except ImportError:
    print("error importing")

import time

button = digitalio.DigitalInOut(board.G0)
print(button)
button.direction = digitalio.Direction.INPUT
print("testing")
print(button.value)
