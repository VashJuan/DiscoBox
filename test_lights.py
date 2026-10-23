# SPDX-FileCopyrightText: 2026 John Cornelison for Vashon Software
# SPDX-License-Identifier: MIT

"""Look at each panel animation on its own: no sound, sensors or servo

To run: copy this file to the board as code.py (it runs instead of main.py).
Delete code.py from the board to go back to the normal show.

Shows every animation in lights.py for SECONDS each. The serial console prints
each name, and whether it is in the show. To add or drop one from the show,
edit SHOW at the top of lights.py.
"""

import time

import board
from digitalio import DigitalInOut

import lights

SECONDS = 8  # how long to show each animation

# the NeoPixel panel is powered by the external power switch, like the amplifier
external_power = DigitalInOut(board.EXTERNAL_POWER)
external_power.switch_to_output(value=True)

pixels = lights.setup_pixels()
animations = lights.make_animations(pixels)

while True:
    for number, (name, animation) in enumerate(animations, 1):
        print(
            "{}. {} ({})".format(
                number, name, "in the show" if name in lights.SHOW else "switched off"
            )
        )
        pixels.fill(0)
        end = time.monotonic() + SECONDS
        while time.monotonic() < end:
            animation.animate()
