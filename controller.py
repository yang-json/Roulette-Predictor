import math
from predictor import Predictor


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

    @staticmethod
    def __read_button(self):
        pass

    @staticmethod
    def __output_result(self):
        pass
