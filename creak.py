# SPDX-FileCopyrightText: 2026 John Cornelison for Vashon Software
# SPDX-License-Identifier: MIT

"""Cartoon door creak: a raspy synth tone that follows how fast the door swings

The Feather is mounted on the door, so the direction of gravity seen by the
accelerometer turns as the door swings. The angle it turns per second sets the
creak's pitch, rasp & volume. No calibration needed: it works whichever way the
board is mounted.
"""

import array
import math
import time

import synthio

from config import verbose
from sound import MIXER_SAMPLE_RATE, MIXER_CHANNELS

# Tuning: degrees per second of door swing
QUIET_SPEED = 20  # slower than this is silent (accelerometer noise ~5 deg/s)
LOUD_SPEED = 200  # a brisk swing; faster than this is full creak
MEASURE_EVERY = 0.08  # seconds between speed measurements
SMOOTHING = 0.3  # 0..1, how much each accelerometer reading moves the average

# Creak sound at QUIET_SPEED .. LOUD_SPEED
PITCH = (55, 140)  # Hz
RASP = (12, 35)  # clicks per second
MAX_LEVEL = 0.9  # mixer volume at full creak


def map_range(s, a1, a2, b1, b2):
    """Like Arduino map(), but clamped to b1..b2"""
    s = min(max(s, a1), a2)
    return b1 + ((s - a1) * (b2 - b1) / (a2 - a1))


class DoorCreak:
    """Plays on mixer voice 1, over the song on voice 0"""

    def __init__(self, mixer):
        self.voice = mixer.voice[1]
        self.voice.level = 0
        synth = synthio.Synthesizer(
            channel_count=MIXER_CHANNELS, sample_rate=MIXER_SAMPLE_RATE
        )
        # downward saw: bright & buzzy
        saw = array.array("h", [int(30000 - 60000 * i / 64) for i in range(64)])
        # short pulses on the volume make the stick-slip "rasp" of a hinge
        clicks = array.array("h", [32767, 20000, 0, 0, 0, 0])
        self.rasp = synthio.LFO(waveform=clicks, rate=RASP[0], interpolate=False)
        self.note = synthio.Note(frequency=PITCH[0], waveform=saw, amplitude=self.rasp)
        synth.press(self.note)
        self.voice.play(synth)

        self.gravity = None  # smoothed gravity direction
        self.last_gravity = None
        self.last_time = 0

    def update(self, x, y, z):
        """Call often with the accelerometer reading (in G)"""
        if self.gravity is None:
            self.gravity = [x, y, z]
            self.last_gravity = list(self.gravity)
            self.last_time = time.monotonic()
            return
        g = self.gravity
        for i, value in enumerate((x, y, z)):
            g[i] += SMOOTHING * (value - g[i])

        now = time.monotonic()
        elapsed = now - self.last_time
        if elapsed < MEASURE_EVERY:
            return
        speed = math.degrees(angle_between(self.last_gravity, g)) / elapsed
        self.last_gravity = list(g)
        self.last_time = now

        if speed < QUIET_SPEED:
            self.voice.level = 0
            return
        self.note.frequency = map_range(speed, QUIET_SPEED, LOUD_SPEED, *PITCH)
        self.rasp.rate = map_range(speed, QUIET_SPEED, LOUD_SPEED, *RASP)
        self.voice.level = map_range(speed, QUIET_SPEED, LOUD_SPEED, 0.2, MAX_LEVEL)
        if verbose:
            print("Creak: {:.0f} deg/s".format(speed))


def angle_between(a, b):
    """Angle in radians between two 3D vectors"""
    dot = a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
    lengths = math.sqrt(
        (a[0] ** 2 + a[1] ** 2 + a[2] ** 2) * (b[0] ** 2 + b[1] ** 2 + b[2] ** 2)
    )
    if lengths == 0:
        return 0
    return math.acos(min(max(dot / lengths, -1), 1))
