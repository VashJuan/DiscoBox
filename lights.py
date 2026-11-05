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

from config import theme_settings, led_max

num_pixels = 64
anim_speed = 0.1
brightness = 0.05  # panel brightness when the lights don't follow the music

# Animations in the show come from the theme (themes/*.py); drop a name there to switch one off
SHOW = theme_settings.SHOW

# Halloween colours
PUMPKIN = (255, 50, 0)
GHOUL = (40, 255, 0)  # ghoulish green

# Thanksgiving colours: fall leaves, with the Pacific Northwest's cold & rain
LEAF_COLORS = ((255, 90, 0), (255, 150, 0), (200, 40, 0), (150, 0, 15), (120, 50, 0))
RUST = (200, 40, 0)
CRANBERRY = (150, 0, 15)
ICE = (110, 190, 255)  # a raindrop or frost: pale cold blue
COLD_BLUE = (0, 60, 255)
SLATE = (6, 8, 16)  # a rain-cloud sky, just lit
TOP_ROW = 0  # the panel row where rain & leaves start; 7 if they fall upwards

# Lightning: white flashes as a chime starts (when the theme has LIGHTNING:
# True for every chime, or a tuple of chime names, e.g. ("thunder",))
FLASHES = ((0, 0.06), (0.14, 0.3))  # seconds from the start: (on, off)
FLASH_BRIGHTNESS = 0.5
FLASH_COLOR = getattr(theme_settings, "LIGHTNING_COLOR", (255, 255, 255))

# Lights follow the music (MusicPulse): brightness rises with each beat, then fades
PULSE_MIN = 0.02  # brightness in quiet moments
PULSE_MAX = led_max  # brightness on the loudest beats (config.py)
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
        # Thanksgiving
        ("leaf fall", lambda: LeafFall(pixels, speed=anim_speed)),
        (
            "leaves in the rain",
            lambda: LeafFall(pixels, speed=anim_speed, raindrops=3),
        ),
        (
            "harvest pulse",
            lambda: Pulse(pixels, speed=anim_speed, color=RUST, period=4),
        ),
        (
            "cranberry comet rows",
            lambda: Comet(
                pixel_wing_horizontal,
                speed=anim_speed,
                color=CRANBERRY,
                tail_length=6,
                bounce=True,
            ),
        ),
        ("cold front", lambda: ColdFront(pixels, speed=anim_speed)),
        (
            "ice sparkle",
            lambda: Sparkle(pixels, speed=anim_speed, color=ICE, num_sparkles=4),
        ),
        ("drizzle", lambda: Rain(pixels, speed=anim_speed, drops=4, fall=(0.5, 0.8))),
        ("downpour", lambda: Rain(pixels, speed=anim_speed, drops=12, fall=(0.8, 1.3))),
        ("storm", lambda: Storm(pixels, speed=anim_speed)),
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


def at(x, y):
    """Pixel index of column x, row y (rows run from TOP_ROW, the top)"""
    return (y if TOP_ROW == 0 else 7 - y) * 8 + x


def dim(rgb, share):
    """rgb at share (0-1) of its brightness"""
    return (int(rgb[0] * share), int(rgb[1] * share), int(rgb[2] * share))


class Drop:
    """One falling thing (a raindrop or a leaf): a column, a row and a speed"""

    def __init__(self, fall, color, sway=0):
        self.fall = fall  # (slowest, fastest) rows per frame
        self.color = color
        self.sway = sway  # columns a leaf drifts either way
        self.restart()
        self.y = random.uniform(-8, 7)  # spread out at first

    def restart(self):
        self.x0 = random.randint(0, 7)
        self.y = random.uniform(-4, 0)  # a moment above the panel first
        self.speed = random.uniform(*self.fall)
        self.phase = random.uniform(0, 6.3)

    def step(self):
        """Moves down; returns the column it lands in, or None"""
        self.y += self.speed
        if self.y < 8:
            return None
        landed = self.column()
        self.restart()
        return landed

    def column(self):
        drift = self.sway * math.sin(self.phase + self.y * 0.9)
        return min(max(int(self.x0 + drift + 0.5), 0), 7)


class Rain(Animation):
    """Pale blue raindrops streaking down a dark sky, splashing at the bottom"""

    def __init__(self, pixel_object, speed, drops, fall):
        super().__init__(pixel_object, speed, ICE)
        self.drops = [Drop(fall, ICE) for _ in range(drops)]
        self.splashes = [0.0] * 8  # how bright each column's splash still is

    def draw(self):
        self.pixel_object.fill(SLATE)
        for x, splash in enumerate(self.splashes):
            if splash > 0.05:
                self.pixel_object[at(x, 7)] = dim(ICE, splash)
            self.splashes[x] = splash * 0.5
        for drop in self.drops:
            landed = drop.step()
            if landed is not None:
                self.splashes[landed] = 0.8
            elif drop.y >= 0:
                y = int(drop.y)
                self.pixel_object[at(drop.x0, y)] = ICE
                if y > 0:
                    self.pixel_object[at(drop.x0, y - 1)] = dim(COLD_BLUE, 0.5)


class LeafFall(Animation):
    """Fall leaves drifting down and piling up at the bottom, maybe in the rain"""

    def __init__(self, pixel_object, speed, raindrops=0):
        super().__init__(pixel_object, speed, LEAF_COLORS[0])
        self.leaves = [
            Drop((0.12, 0.3), random.choice(LEAF_COLORS), sway=1.2) for _ in range(5)
        ]
        self.rain = [Drop((0.8, 1.2), ICE) for _ in range(raindrops)]
        self.pile = [None] * 8  # the leaf colour lying in each bottom pixel

    def draw(self):
        self.pixel_object.fill(0)
        for x, color in enumerate(self.pile):
            if color:
                self.pixel_object[at(x, 7)] = dim(color, 0.4)
        for drop in self.rain:
            drop.step()
            if drop.y >= 0:
                self.pixel_object[at(drop.x0, int(drop.y))] = dim(ICE, 0.7)
        for leaf in self.leaves:
            landed = leaf.step()
            if landed is not None:
                self.pile[landed] = leaf.color
                leaf.color = random.choice(LEAF_COLORS)
            elif leaf.y >= 0:
                self.pixel_object[at(leaf.column(), int(leaf.y))] = leaf.color
        if random.random() < 0.02:  # now & then the wind clears a leaf away
            self.pile[random.randint(0, 7)] = None


class ColdFront(Animation):
    """Fall colours, with a band of cold blue pushing in from one side and back"""

    PERIOD = 8  # seconds for the cold to come in and go out again

    def __init__(self, pixel_object, speed):
        super().__init__(pixel_object, speed, COLD_BLUE)
        self.warm = [random.choice(LEAF_COLORS) for _ in range(64)]

    def draw(self):
        # how far in the cold has come: 0 to 5 columns
        reach = 2.5 * (1 - math.cos(2 * math.pi * time.monotonic() / self.PERIOD))
        if random.random() < 0.3:  # the leaves shift a little
            self.warm[random.randint(0, 63)] = random.choice(LEAF_COLORS)
        for x in range(8):
            cold = min(max(reach - x, 0.0), 1.0)  # 1 = all blue, 0 = all fall
            for y in range(8):
                warm = self.warm[y * 8 + x]
                self.pixel_object[at(x, y)] = (
                    int(warm[0] * (1 - cold) + COLD_BLUE[0] * cold),
                    int(warm[1] * (1 - cold) + COLD_BLUE[1] * cold),
                    int(warm[2] * (1 - cold) + COLD_BLUE[2] * cold),
                )


class Storm(Animation):
    """Dark clouds rolling over, lit now & then from inside by lightning"""

    def __init__(self, pixel_object, speed):
        super().__init__(pixel_object, speed, ICE)
        self.clouds = [random.random() for _ in range(64)]
        self.flash = 0  # frames of lightning left

    def draw(self):
        if self.flash == 0 and random.random() < 0.03:
            self.flash = random.randint(1, 3)
        if self.flash:
            self.flash -= 1
            # a flicker of cold white, brightest at the top
            for y in range(8):
                for x in range(8):
                    self.pixel_object[at(x, y)] = dim(ICE, 1 - y * 0.08)
            return
        # clouds drift sideways a column at a time, changing as they go
        self.clouds = self.clouds[1:] + self.clouds[:1]
        for i in range(64):
            cloud = min(max(self.clouds[i] + random.uniform(-0.1, 0.1), 0.0), 1.0)
            self.clouds[i] = cloud
            self.pixel_object[i] = dim((20, 26, 60), 0.2 + 0.8 * cloud)


class Lightning:
    """A double flash over the panel; update() is True while it flashes

    It flashes for every chime, or with LIGHTNING a tuple of chime names
    (themes/*.py), only for those.
    """

    def __init__(self, pixels):
        self.pixels = pixels
        self.start_time = None
        self.brightness = pixels.brightness
        lightning = theme_settings.LIGHTNING
        self.chimes = lightning if isinstance(lightning, tuple) else None

    def start(self, chime=None):
        """Flash now; chime is the name of the chime that set it off"""
        if self.chimes is not None and chime not in self.chimes:
            return
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
        self.pixels.fill(FLASH_COLOR if lit else 0)
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
