# SPDX-FileCopyrightText: 2023 John Cornelison for Vashon Software
# SPDX-License-Identifier: MIT

"""Servo motor on the Prop-Maker's servo header"""

import board
import pwmio
from adafruit_motor import servo


class ServoSweep:
    """Move the servo back and forth, 5 degrees per step"""

    def __init__(self):
        pwm = pwmio.PWMOut(board.EXTERNAL_SERVO, duty_cycle=2**15, frequency=50)
        self.servo = servo.Servo(pwm)
        self.angle = 0
        self.angle_plus = True

    def step(self):
        self.servo.angle = self.angle
        if self.angle_plus:
            self.angle += 5
        else:
            self.angle -= 5
        if self.angle == 180:
            self.angle_plus = False
        elif self.angle == 0:
            self.angle_plus = True
