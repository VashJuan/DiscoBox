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

import math
import random
import time

import board
import neopixel
from adafruit_led_animation.animation.rainbow import Rainbow
from adafruit_led_animation.animation.comet import Comet
from adafruit_led_animation.animation.rainbowcomet import RainbowComet
from adafruit_led_animation.animation.rainbowchase import RainbowChase
from adafruit_led_animation.animation.rainbowsparkle import RainbowSparkle
from adafruit_led_animation.animation.chase import Chase
from adafruit_led_animation.animation.pulse import Pulse
from adafruit_led_animation.animation.sparkle import Sparkle
from adafruit_led_animation.animation import Animation
from adafruit_led_animation.sequence import AnimationSequence
from adafruit_led_animation import helper

import adafruit_led_animation.color as color  # now we can use color.RED, etc.

from config import theme_settings

num_pixels = 64
anim_speed = 0.1
brightness = 0.05  # panel brightness when the lights don't follow the music

# Animations in the show come from the theme (themes/*.py); drop a name there to switch one off
SHOW = theme_settings.SHOW

# Halloween colours
PUMPKIN = (255, 50, 0)
GHOUL = (40, 255, 0)  # ghoulish green

# Lightning: white flashes as a chime starts (when the theme has LIGHTNING)
FLASHES = ((0, 0.06), (0.14, 0.3))  # seconds from the start: (on, off)
FLASH_BRIGHTNESS = 0.5

# Lights follow the music (MusicPulse): brightness rises with each beat, then fades
PULSE_MIN = 0.02  # brightness in quiet moments
PULSE_MAX = 0.25  # brightness on the loudest beats
PULSE_FADE = 0.15  # seconds for a pulse to fade by ~2/3 (rises are instant)
PEAK_FADE = 4.0  # seconds for the loudness reference to settle after a loud part
BEAT_FLOOR = 0.8  # 0-1; loudness below this share of the recent average stays dim
PULSE_FRAME = 0.02  # redraw the panel at most every 20 ms


def setup_status_led():
    """The single NeoPixel on the Feather itself"""
    return neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.1)


def setup_pixels():
    """The external 8x8 panel"""
    return neopixel.NeoPixel(
        board.EXTERNAL_NEOPIXELS, num_pixels, brightness=brightness, auto_write=False
    )


def make_animations(pixels, names=None):
    """Panel animations as a list of (name, animation); all of them, or just names"""
    pixel_wing_vertical = helper.PixelMap.vertical_lines(
        pixels, 8, 8, helper.horizontal_strip_gridmap(8, alternating=False)
    )
    pixel_wing_horizontal = helper.PixelMap.horizontal_lines(
        pixels, 8, 8, helper.horizontal_strip_gridmap(8, alternating=False)
    )
    makers = [
        ("rainbow", lambda: Rainbow(pixel_wing_vertical, speed=anim_speed, period=2)),
        (
            "rainbow comet",
            lambda: RainbowComet(
                pixel_wing_vertical, speed=anim_speed, tail_length=7, bounce=True
            ),
        ),
        (
            "rainbow chase columns",
            lambda: RainbowChase(
                pixel_wing_vertical, speed=anim_speed, size=7, spacing=2, step=8
            ),
        ),
        (
            "rainbow chase pixels",
            lambda: RainbowChase(pixels, speed=anim_speed, size=3, spacing=3),
        ),
        (
            "rainbow sparkle",
            lambda: RainbowSparkle(pixels, speed=anim_speed, num_sparkles=10),
        ),
        (
            "purple comet rows",
            lambda: Comet(
                pixel_wing_horizontal,
                speed=anim_speed,
                color=color.PURPLE,
                tail_length=7,
                bounce=True,
            ),
        ),
        (
            "amber comet columns",
            lambda: Comet(
                pixel_wing_vertical,
                speed=anim_speed,
                color=color.AMBER,
                tail_length=6,
                bounce=True,
            ),
        ),
        (
            "jade chase rows",
            lambda: Chase(
                pixel_wing_horizontal,
                speed=anim_speed,
                size=7,
                spacing=6,
                color=color.JADE,
            ),
        ),
        # Halloween
        (
            "pumpkin comet columns",
            lambda: Comet(
                pixel_wing_vertical,
                speed=anim_speed,
                color=PUMPKIN,
                tail_length=6,
                bounce=True,
            ),
        ),
        (
            "pumpkin pulse",
            lambda: Pulse(pixels, speed=anim_speed, color=PUMPKIN, period=3),
        ),
        ("candle flicker", lambda: CandleFlicker(pixels, speed=anim_speed)),
        (
            "purple chase rows",
            lambda: Chase(
                pixel_wing_horizontal,
                speed=anim_speed * 1.5,
                size=2,
                spacing=3,
                color=color.PURPLE,
            ),
        ),
        (
            "ghoul sparkle",
            lambda: Sparkle(pixels, speed=anim_speed, color=GHOUL, num_sparkles=6),
        ),
        (
            "ghoul comet rows",
            lambda: Comet(
                pixel_wing_horizontal,
                speed=anim_speed,
                color=GHOUL,
                tail_length=5,
                bounce=True,
            ),
        ),
    ]
    return [
        (name, make()) for name, make in makers if names is None or name in names
    ]


class CandleFlicker(Animation):
    """Every pixel a candle flame: orange to yellow, each flickering on its own"""

    def __init__(self, pixel_object, speed):
        super().__init__(pixel_object, speed, PUMPKIN)
        self.flames = [random.random() for _ in range(len(pixel_object))]

    def draw(self):
        for i, flame in enumerate(self.flames):
            flame = min(max(flame + random.uniform(-0.35, 0.35), 0.15), 1.0)
            self.flames[i] = flame
            self.pixel_object[i] = (
                int(255 * flame), int((30 + 90 * flame) * flame), 0
            )


class Lightning:
    """A double white flash over the panel; update() is True while it flashes"""

    def __init__(self, pixels):
        self.pixels = pixels
        self.start_time = None
        self.brightness = pixels.brightness

    def start(self):
        if self.start_time is None:
            self.brightness = self.pixels.brightness
        self.start_time = time.monotonic()

    def update(self):
        """Call often; while it returns True, skip the animations"""
        if self.start_time is None:
            return False
        elapsed = time.monotonic() - self.start_time
        if elapsed >= FLASHES[-1][1]:
            self.start_time = None
            self.pixels.fill(0)
            self.pixels.brightness = self.brightness
            self.pixels.show()
            return False
        lit = any(on <= elapsed < off for on, off in FLASHES)
        self.pixels.brightness = FLASH_BRIGHTNESS
        self.pixels.fill((255, 255, 255) if lit else 0)
        self.pixels.show()
        return True


def setup_animations():
    """Build the show's animation sequence; returns (sequence, pixels)"""
    pixels = setup_pixels()
    shown = [anim for name, anim in make_animations(pixels, SHOW)]
    sequence = AnimationSequence(*shown, advance_interval=5, random_order=True)
    return sequence, pixels


class MusicPulse:
    """Sets the panel's brightness from the song's loudness, so it pulses with the beat

    decoder.rms_level is the loudness of the audio the MP3 decoder just made
    (about 0-700 on our clips; Beat It averages ~430, beats ~550-650).
    Each reading is compared with the recent loudest, so quiet and loud songs
    both pulse; quiet moments sit at PULSE_MIN and beats flash towards PULSE_MAX.
    """

    def __init__(self, pixels, decoder):
        self.pixels = pixels
        self.decoder = decoder
        self.peak = 0.0  # recent loudest reading, slowly fading
        self.average = 0.0  # recent average reading
        self.loudest = 0.0  # loudest since power-up; keeps silence dark
        self.level = 0.0  # 0-1, smoothed
        self.last_time = time.monotonic()

    def update(self):
        """Call often while a song plays"""
        now = time.monotonic()
        elapsed = now - self.last_time
        if elapsed < PULSE_FRAME:
            return
        self.last_time = now
        rms = self.decoder.rms_level
        self.loudest = max(self.loudest, rms)
        self.peak = max(
            rms, self.loudest * 0.1, self.peak * math.exp(-elapsed / PEAK_FADE)
        )
        self.average += (rms - self.average) * min(1.0, elapsed / 1.0)
        floor = self.average * BEAT_FLOOR
        if self.peak > floor:
            loudness = min(max((rms - floor) / (self.peak - floor), 0.0), 1.0)
        else:
            loudness = 0.0
        self.level = max(loudness, self.level * math.exp(-elapsed / PULSE_FADE))
        level = PULSE_MIN + (PULSE_MAX - PULSE_MIN) * self.level
        if abs(level - self.pixels.brightness) > 0.003:
            self.pixels.brightness = level
            self.pixels.show()
