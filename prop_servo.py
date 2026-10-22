# SPDX-FileCopyrightText: 2023 John Cornelison for Vashon Software
# SPDX-License-Identifier: MIT

"""Servo motor on the Prop-Maker's servo header"""

import time

import board
import pwmio
from adafruit_motor import servo


class ServoSweep:
    """Move the servo back and forth, 5 degrees per step"""

    step_interval = 0.03  # seconds per 5 degree step: ~1 s per sweep (0.2 was too slow to hear)

    def __init__(self):
        pwm = pwmio.PWMOut(board.EXTERNAL_SERVO, duty_cycle=2**15, frequency=50)
        self.servo = servo.Servo(pwm)
        self.angle = 0
        self.angle_plus = True
        self.last_step = 0

    def step(self):
        now = time.monotonic()
        if now - self.last_step < self.step_interval:
            return
        self.last_step = now
        self.servo.angle = self.angle
        if self.angle_plus:
            self.angle += 5
        else:
            self.angle -= 5
        if self.angle == 180:
            self.angle_plus = False
        elif self.angle == 0:
            self.angle_plus = True
