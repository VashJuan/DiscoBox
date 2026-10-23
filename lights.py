# SPDX-FileCopyrightText: 2023 John Cornelison for Vashon Software
# SPDX-License-Identifier: MIT

"""Onboard status NeoPixel & external 8x8 NeoPixel panel animations

Colors defined by Adafruit Led Animation library:
    https://docs.circuitpython.org/projects/led-animation/en/latest/api.html#adafruit-led-animation-color
    Amber, Aqua, Black, Blue, Cyan, Gold, Green, Jade, Magenta,
    Old lace, Orange, Pink, Purple, Red, Teal, White, Yellow

    Old lace = warm white
    Black = off
    RAINBOW is a list of colors to use for cycling through Includes,
    in order: red, orange, yellow, green, blue, and purple
    RGBW_WHITE_RGB is for RGBW strips to illuminate only the RGB diodes
    RGBW_WHITE_RGBW is for RGBW strips to illuminate the RGB and White diodes
    RGBW_WHITE_W is for RGBW strips to illuminate only White diode
"""

# https://learn.adafruit.com/circuitpython-led-animations
# https://learn.adafruit.com/adafruit-neopixel-uberguide
# https://learn.adafruit.com/adafruit-neopixel-uberguide/neomatrix-library
# TODO: http://fastled.io/
# TODO: https://learn.adafruit.com/adafruit-neopixel-uberguide/advanced-coding

import board
import neopixel
from adafruit_led_animation.animation.rainbow import Rainbow
from adafruit_led_animation.animation.comet import Comet
from adafruit_led_animation.animation.rainbowcomet import RainbowComet
from adafruit_led_animation.animation.rainbowchase import RainbowChase
from adafruit_led_animation.animation.rainbowsparkle import RainbowSparkle
from adafruit_led_animation.animation.chase import Chase
from adafruit_led_animation.sequence import AnimationSequence
from adafruit_led_animation import helper

import adafruit_led_animation.color as color  # now we can use color.RED, etc.

num_pixels = 64
anim_speed = 0.1


def setup_status_led():
    """The single NeoPixel on the Feather itself"""
    return neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.1)


def setup_animations():
    """Build the animation sequence for the external 8x8 panel"""
    pixels = neopixel.NeoPixel(
        board.EXTERNAL_NEOPIXELS, num_pixels, brightness=0.05, auto_write=False
    )

    pixel_wing_vertical = helper.PixelMap.vertical_lines(
        pixels, 8, 8, helper.horizontal_strip_gridmap(8, alternating=False)
    )
    pixel_wing_horizontal = helper.PixelMap.horizontal_lines(
        pixels, 8, 8, helper.horizontal_strip_gridmap(8, alternating=False)
    )
    comet_h = Comet(
        pixel_wing_horizontal,
        speed=anim_speed,
        color=color.PURPLE,
        tail_length=7,
        bounce=True,
    )
    comet_v = Comet(
        pixel_wing_vertical,
        speed=anim_speed,
        color=color.AMBER,
        tail_length=6,
        bounce=True,
    )
    chase_h = Chase(
        pixel_wing_horizontal, speed=anim_speed, size=7, spacing=6, color=color.JADE
    )
    rainbow_chase_v = RainbowChase(
        pixel_wing_vertical, speed=anim_speed, size=7, spacing=2, step=8
    )
    rainbow_comet_v = RainbowComet(
        pixel_wing_vertical, speed=anim_speed, tail_length=7, bounce=True
    )
    rainbow_v = Rainbow(pixel_wing_vertical, speed=anim_speed, period=2)
    rainbow_chase_h = RainbowChase(pixels, speed=anim_speed, size=3, spacing=3)
    rainbow_sparkle = RainbowSparkle(pixels, speed=anim_speed, num_sparkles=10)

    # Customize animation sequence/effects
    return AnimationSequence(
        rainbow_v,
        #    comet_h,
        rainbow_comet_v,
        #    chase_h,
        rainbow_chase_v,
        #    comet_v,
        rainbow_chase_h,
        rainbow_sparkle,
        advance_interval=5,
        random_order=True,
    )
