# SPDX-FileCopyrightText: 2026 John Cornelison for Vashon Software
# SPDX-License-Identifier: MIT

"""Slide whistle: a tone that glides with the distance reading

The VL53L1X sits at the back of the box facing the door, so a hand or mail
moving through the beam changes the reading. While it changes, the whistle
plays: high when near, low when far, gliding between readings. Once readings
stop changing (or nothing is in range) it fades out.
"""

import array
import math
import time

import synthio

from config import verbose
from sound import MIXER_SAMPLE_RATE, MIXER_CHANNELS
from creak import map_range

# Tuning
NEAR, FAR = 3, 130  # cm; the sensor's short-range limits
PITCH = (1800, 500)  # Hz at NEAR, FAR
MOVE_CM = 3  # a reading this much different from the last counts as movement
HOLD = 0.4  # seconds the whistle keeps playing after the last movement
GLIDE = 0.15  # seconds to slide most of the way to a new pitch
LEVEL = 0.5  # mixer volume


class SlideWhistle:
    """Plays on mixer voice 2, over the song (voice 0) & the creak (voice 1)"""

    def __init__(self, mixer):
        self.voice = mixer.voice[2]
        self.voice.level = LEVEL
        self.synth = synthio.Synthesizer(
            channel_count=MIXER_CHANNELS, sample_rate=MIXER_SAMPLE_RATE
        )
        sine = array.array(
            "h", [int(30000 * math.sin(2 * math.pi * i / 64)) for i in range(64)]
        )
        # soft start & fade-out, so the whistle doesn't click on and off
        envelope = synthio.Envelope(attack_time=0.05, release_time=0.25)
        self.note = synthio.Note(
            frequency=PITCH[1], waveform=sine, envelope=envelope
        )
        self.voice.play(self.synth)

        self.last_distance = None
        self.target = PITCH[1]
        self.playing = False
        self.last_move = 0
        self.last_time = time.monotonic()

    def distance(self, cm):
        """Call with each new reading: cm, or None when nothing is in range"""
        last, self.last_distance = self.last_distance, cm
        if cm is not None:
            self.target = map_range(cm, NEAR, FAR, *PITCH)
        moved = (cm is None) != (last is None) or (
            cm is not None and abs(cm - last) >= MOVE_CM
        )
        if not moved:
            return
        self.last_move = time.monotonic()
        if verbose:
            print("Whistle: {} cm".format(cm))
        if cm is not None and not self.playing:
            self.note.frequency = self.target  # start at the reading, no swoop
            self.synth.press(self.note)
            self.playing = True

    def update(self):
        """Call often: glides the pitch & stops the whistle once still"""
        now = time.monotonic()
        elapsed, self.last_time = now - self.last_time, now
        if not self.playing:
            return
        if now - self.last_move > HOLD or self.last_distance is None:
            self.synth.release(self.note)
            self.playing = False
            return
        step = min(elapsed / GLIDE, 1)
        self.note.frequency += step * (self.target - self.note.frequency)
