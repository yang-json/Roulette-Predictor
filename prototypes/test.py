import numpy as np
import keyboard
from datetime import datetime


class Predictor:
    def __init__(self, r_rim, r_defl, alpha, sectors):
        self.r_rim = r_rim
        self.r_defl = r_defl
        self.alpha = alpha
        self.g = 9.81
        self.sectors = sectors

        self.time_stamps = []

    def get_time_stamps(self):
        self.time_stamps.append(datetime.now())

    def play(self):
        while True:
            self.time_stamps = []
            for i in range(3):
                keyboard.on_press(self.get_time_stamps)
                keyboard.wait('esc')
                print(f"Sector {self.prediction()}")


    def predict(self):
        self.get_initial_values()
        self.time_step()
        return np.floor(self.get_position() * (self.sectors / (2 * np.pi)))

    def get_initial_values(self, start, half, full):
        split1 = self.time_stamps[1] - self.time_stamps[0]
        split2 = self.time_stamps[2] - self.time_stamps[1]
        speed_half = (np.pi * self.r_rim) / split1
        self.pos_0 = 0
        self.vel_0 = (np.pi * self.r_rim) / split2
        self.acc_0 = (self.vel_0 - speed_half) / split2

    def time_step(self, dt=0.01):
        t = 0
        r = self.r_rim
        while r > self.r_defl:
            vel = self.vel_0 + self.alpha * t
            r += (
                r * vel**2 * np.cos(self.alpha) * dt
                - self.g * np.sin(self.alpha) * dt
            )
            t += dt

        self.t_defl = t

    def get_position(self):
        pos_t_defl = (
            self.pos_0 + self.vel_0 * self.t_defl + 0.5 * self.acc_0 * self.t_defl**2
        )
        return abs(pos_t_defl) % (2 * np.pi)


if __name__ == "__main__":
    r_rim = 60
    r_defl = 45
    alpha = 10
    sectors = 12
    Predictor(r_rim, r_defl, alpha, sectors).play()
