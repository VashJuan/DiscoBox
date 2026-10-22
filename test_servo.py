# SPDX-FileCopyrightText: 2026 John Cornelison for Vashon Software
# SPDX-License-Identifier: MIT

"""Test the servo on its own: no sound, lights or sensors

To run: copy this file to the board as code.py (it runs instead of main.py).
Delete code.py from the board to go back to the normal show.

Moves the servo to 0, 90 & 180 degrees, 2 s at each, then sweeps it the way
main.py does. The serial console shows each angle.
"""

import time

import board
from digitalio import DigitalInOut

from prop_servo import ServoSweep

# the servo header is powered by the external power switch, like the amplifier
external_power = DigitalInOut(board.EXTERNAL_POWER)
external_power.switch_to_output(value=True)

prop_servo = ServoSweep()
for angle in (0, 90, 180, 90):
    print("Angle", angle)
    prop_servo.servo.angle = angle
    time.sleep(2)

print("Sweeping")
last_angle = None
while True:
    prop_servo.step()
    if prop_servo.angle != last_angle and prop_servo.angle in (0, 180):
        print("Angle", prop_servo.angle)
    last_angle = prop_servo.angle
    time.sleep(0.01)
