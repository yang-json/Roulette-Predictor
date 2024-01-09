import math

g = 9.81
R_RIM = 0.2
R_DEFL = 0.1575
ALPHA = 0.247


class Predictor:
    def __init__(self):
        self.dot_theta_0 = None
        self.dot_theta_rim = None
        self.ddot_theta_0 = None

        self.dot_phi = None

        self.t_rim = None
        self.t_ramp = None

        self.measuring_wheel = True

    def predict_round(self, splits):
        """
        Controls the prediction round
        """

        self.get_parameters(splits)
        self.rim_motion()
        self.time_step()
        return self.compute_radian()

    def get_parameters(self, splits):
        """
        Stores parameters, based on timestamps
        """
        speed_lap_1 = 2 * math.pi / splits[0]

        self.dot_theta_0 = 2 * math.pi / splits[1]
        self.ddot_theta_0 = (self.dot_theta_0 - speed_lap_1) / splits[1]

        # Also measuring wheel
        if len(splits) == 3:
            self.dot_phi = 2 * math.pi / splits[2]

        # Only measuring ball
        else:
            self.measuring_wheel = False

    def rim_motion(self):
        """
        Computes and stores the time it takes the ball to leave the rim
        and the speed it has
        """
        dot_theta_rim = math.sqrt((g * math.tan(ALPHA)) / R_RIM)
        minus = self.dot_theta_0 - dot_theta_rim
        minus = (-1 / self.ddot_theta_0) * minus

        self.t_rim = minus
        self.dot_theta_rim = dot_theta_rim

    def time_step(self):
        """
        Computes and stores the time
        it takes the ball from the rim to the deflector
        """

        t = 0
        dt = 0.01
        r = R_RIM
        dot_r = 0
        ddot_r = 0

        ddot_theta_rim = self.ddot_theta_0
        dot_theta_rim = self.dot_theta_rim

        while r > R_DEFL:
            dot_theta_rim += ddot_theta_rim * dt
            ddot_r += r * math.cos(ALPHA) * dot_theta_rim**2 - g * math.sin(ALPHA)
            dot_r += ddot_r * dt
            r += dot_r * dt
            t += dt

        self.t_ramp = t

    def compute_radian(self):
        """
        Computer and stores the result of the prediction
        """
        t_defl = self.t_rim + self.t_ramp

        theta_defl = self.dot_theta_0 * t_defl + 0.5 * self.ddot_theta_0 * t_defl**2
        if self.measuring_wheel:
            salient = theta_defl - self.dot_phi * t_defl
        else:
            salient = theta_defl

        return (salient % (2 * math.pi)) / (2 * math.pi)
