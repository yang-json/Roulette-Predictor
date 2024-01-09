import time
import math
from machine import Pin
from predictor import Predictor

butt = Pin(0, Pin.IN, Pin.PULL_UP)
temp1 = Pin(3, Pin.IN, None)
temp2 = Pin(4, Pin.IN, None)
vib1 = Pin(5, Pin.OUT)
vib2 = Pin(2, Pin.OUT)
vib1.value(0)
vib2.value(0)

def waitForButton():
    while butt.value() == 1:
        continue
    output = time.time_ns() // 1000000
    time.sleep_ms(30)
    while butt.value() == 0:
        continue
    time.sleep_ms(30)
    return output

def vibOutput(num, totalNum):
    iters = max(1, (1 + math.log2(totalNum)) // 2)
    for _ in range(iters):
        val1 = num % 2
        print(val1)
        num //= 2
        val2 = num % 2
        print(val2)
        num //= 2
        vib1.value(val1)
        vib2.value(val2)
        time.sleep(1)
        vib1.value(0)
        vib2.value(0)
        time.sleep(.2)
        
    vib1.value(0)
    vib2.value(0)
    
def signalReset():
    for _ in range(4):
        vib1.value(1)
        vib2.value(1)
        time.sleep(.2)
        vib1.value(0)
        vib2.value(0)
        time.sleep(.2)
    
# for _ in range(8):
#     print(f"iter: {_}")
#     signalReset()
#     vibOutput(_, 8)
#     signalReset()
#     time.sleep(1)

#     print('Ready')
#     signalReset()
#     signalReset()
#     while butt.value() == 1:
#         continue
#     start = time.time_ns() // 1000000
#     while butt.value() == 0:
#         continue
#     time.sleep_ms(30)
#     while butt.value() == 1:
#         continue
#     step_1 = time.time_ns() // 1000000
#     time.sleep_ms(30)
#     while butt.value() == 0:
#         continue
#     time.sleep_ms(30)
#     while butt.value() == 1:
#         continue
#     step_2 = time.time_ns() // 1000000
#     print(f'Step 1: {step_1 - start}')
#     print(f'Step 2: {step_2 - step_1}')
#     print()
#     time.sleep(4)
    
    
class Controller:
    def __init__(self, n: int, connected=True):
        self.p = Predictor()
        self.n = n

        if connected:
            self.__loop()

    def __loop(self):
        """
        Controls states of device, reading, processing and signaling
        """
        device_state = 0
        while True:
            # Waiting
            if not device_state:
                _, button_state = Controller.__read_button()

                if button_state:
                    device_state = 1

            # Playing
            else:
                timestamps, button_state = Controller.__read_button()

                if not button_state:  # button was not held
                    sector = self.__get_sector(timestamps)
                    assert (
                        0 <= sector < self.n
                    ), "Sector is not between expected boundaries"
                    Controller.__output_result(sector)
                else:
                    pass

    def __get_sector(self, timestamps):
        ballSplit1 = timestamps[1] - timestamps[0]
        ballSplit2 = timestamps[2] - timestamps[1]
        wheelSplit = timestamps[4] - timestamps[3]
        radians = self.p.predict_round([ballSplit1, ballSplit2, wheelSplit])
        return math.floor(radians * self.n)

    def debug(self, splits):
        radians = self.p.predict_round(splits)
        return math.floor(radians * self.n)

    def __read_button(self):
        print('Ready')
        signalReset()
        signalReset()
        output = []
        for _ in range(5):
            output.append(waitForButton())
        return output     

    def __output_result(self, result):
        iters = max(1, (1 + math.log2(self.n)) // 2)
        for _ in range(iters):
            val1 = result % 2
            print(val1)
            result //= 2
            val2 = result % 2
            print(val2)
            result //= 2
            vib1.value(val1)
            vib2.value(val2)
            time.sleep(1)
            vib1.value(0)
            vib2.value(0)
            time.sleep(.2)
            
        vib1.value(0)
        vib2.value(0)
        
    def __signal_reset(self):
        for _ in range(4):
            vib1.value(1)
            vib2.value(1)
            time.sleep(.2)
            vib1.value(0)
            vib2.value(0)
            time.sleep(.2)