# SPDX-FileCopyrightText: 2026 John Cornelison for Vashon Software
# SPDX-License-Identifier: MIT

"""Door sounds: a hinge squeak while the door swings, a doorbell or boing when still

The Feather is mounted on the door, so the accelerometer sees the direction of
gravity turn as the door swings.
- Squeak: plays while the door moves. Its pitch follows the door's angle, high
  when closed (up) and low when open (down), so it rises as the door goes up and
  falls as it comes down. The faster the swing, the louder and raspier.
- Chimes: while the door stays still, every 30-50 seconds one of: a doorbell
  "ding-dong", a cartoon "boing", a laser "pew pew pew", a frog "ribbit" or a
  flying saucer.
"""

import array
import math
import random
import time

import synthio

from config import verbose
from sound import MIXER_SAMPLE_RATE, MIXER_CHANNELS

# Tuning: degrees per second of door swing
QUIET_SPEED = 20  # slower than this is still (accelerometer noise ~5 deg/s)
LOUD_SPEED = 200  # a brisk swing; faster than this is full squeak
MEASURE_EVERY = 0.08  # seconds between speed measurements
SMOOTHING = 0.3  # 0..1, how much each accelerometer reading moves the average

# Door angle: gravity as the board sees it (in G) with the door closed;
# sensors.py notes y ~= -0.9 closed, y ~= 0 open
CLOSED_GRAVITY = (0, -1, 0)
OPEN_ANGLE = 110  # degrees from closed (vertical) to fully open (~20 deg below level)

# Squeak
PITCH = (1250, 700)  # Hz, door closed .. fully open
RASP = (18, 30)  # clicks per second, slow .. fast swing
LEVEL = (0.2, 0.9)  # volume, slow .. fast swing
GLIDE = 0.15  # seconds for pitch & volume to settle on a new reading

# Chimes while the door is still
CHIME_GAP = (30, 50)  # seconds of stillness before each chime
CHIME_LEVEL = 0.8


def map_range(s, a1, a2, b1, b2):
    """Like Arduino map(), but clamped to b1..b2"""
    s = min(max(s, a1), a2)
    return b1 + ((s - a1) * (b2 - b1) / (a2 - a1))


def wave(shape):
    """64-sample waveform from shape(phase 0..1) -> -1..1"""
    return array.array("h", [int(30000 * shape(i / 64)) for i in range(64)])


SAW = wave(lambda p: 1 - 2 * p)  # bright & buzzy
TRIANGLE = wave(lambda p: 1 - 4 * abs(p - 0.5))
SQUARE = wave(lambda p: 1 if p < 0.5 else -1)
RAMP_UP = array.array("h", [0, 32767])  # LFO shape: 0 to 1 once
# short pulses on the volume make a stick-slip "rasp"
CLICKS = array.array("h", [32767, 20000, 0, 0, 0, 0])
CROAK = array.array("h", [32767, 32767, 32767, 0])  # mostly on: a loud rasp
# a few harmonics, for a brighter bell than a pure sine
BELL = wave(
    lambda p: (
        math.sin(2 * math.pi * p)
        + 0.5 * math.sin(4 * math.pi * p)
        + 0.25 * math.sin(6 * math.pi * p)
    ) / 1.75
)


class Doorbell:
    """Ding-dong: E5 then C5, ringing out"""

    def __init__(self, synth):
        self.synth = synth
        ring = synthio.Envelope(
            attack_time=0.005, decay_time=1.2, sustain_level=0, release_time=0.3
        )
        self.ding = synthio.Note(
            frequency=659, waveform=BELL, envelope=ring, amplitude=CHIME_LEVEL
        )
        self.dong = synthio.Note(
            frequency=523, waveform=BELL, envelope=ring, amplitude=CHIME_LEVEL
        )
        self.start = None

    def play(self):
        self.start = time.monotonic()
        self.synth.press(self.ding)

    def update(self):
        """Returns False once finished"""
        elapsed = time.monotonic() - self.start
        if elapsed >= 2.0:
            self.synth.release((self.ding, self.dong))
            return False
        if elapsed >= 0.5 and self.dong not in self.synth.pressed:
            self.synth.press(self.dong)
        return True


class Boing:
    """Cartoon spring: a wobbling tone that settles"""

    def __init__(self, synth):
        self.synth = synth
        self.wobble = synthio.LFO(rate=14, scale=0.2)  # octaves
        self.note = synthio.Note(
            frequency=392,
            waveform=TRIANGLE,
            bend=self.wobble,
            amplitude=CHIME_LEVEL,
            envelope=synthio.Envelope(
                attack_time=0.005, decay_time=1.0, sustain_level=0, release_time=0.1
            ),
        )
        self.start = None

    def play(self):
        self.start = time.monotonic()
        self.wobble.scale = 0.2
        self.synth.press(self.note)

    def update(self):
        """Returns False once finished"""
        elapsed = time.monotonic() - self.start
        if elapsed >= 1.0:
            self.synth.release(self.note)
            return False
        self.wobble.scale = 0.2 * (1 - elapsed)  # the spring settles
        return True


class Repeats:
    """A short sound played a few times; subclasses make each note"""

    COUNT = 3
    EVERY = 0.2  # seconds from one to the next
    TAIL = 0.3  # seconds after the last one before finishing

    def __init__(self, synth):
        self.synth = synth
        self.note = None
        self.start = None
        self.played = 0

    def make_note(self):
        raise NotImplementedError

    def play(self):
        self.start = time.monotonic()
        self.played = 0
        self.update()

    def update(self):
        """Returns False once finished"""
        elapsed = time.monotonic() - self.start
        if elapsed >= self.EVERY * (self.COUNT - 1) + self.TAIL:
            self.synth.release(self.note)
            return False
        if self.played < self.COUNT and elapsed >= self.EVERY * self.played:
            if self.note:
                self.synth.release(self.note)
            # a fresh note each time, so its one-shot sweep starts over
            self.note = self.make_note()
            self.synth.press(self.note)
            self.played += 1
        return True


class Laser(Repeats):
    """Pew pew pew: three quick zaps, each falling two octaves"""

    def make_note(self):
        return synthio.Note(
            frequency=1800,
            waveform=SQUARE,
            amplitude=CHIME_LEVEL,
            bend=synthio.LFO(waveform=RAMP_UP, rate=1 / 0.15, scale=-2, once=True),
            envelope=synthio.Envelope(
                attack_time=0.002, decay_time=0.15, sustain_level=0, release_time=0.05
            ),
        )


class Frog(Repeats):
    """Ribbit: two raspy croaks that rise a little"""

    COUNT = 2
    EVERY = 0.35
    TAIL = 0.3

    def make_note(self):
        # each croak holds until the next starts (or the tail ends)
        return synthio.Note(
            frequency=500,
            waveform=SQUARE,
            amplitude=synthio.LFO(
                waveform=CROAK, rate=30, scale=1, interpolate=False
            ),
            bend=synthio.LFO(waveform=RAMP_UP, rate=1 / 0.3, scale=0.5, once=True),
            envelope=synthio.Envelope(
                attack_time=0.01, decay_time=0.1, sustain_level=0.9, release_time=0.05
            ),
        )


class Saucer:
    """Flying saucer: a warbling tone that climbs, then fades away"""

    def __init__(self, synth):
        self.synth = synth
        self.note = synthio.Note(
            frequency=500,
            waveform=TRIANGLE,
            bend=synthio.LFO(rate=8, scale=0.12),  # octaves
            amplitude=CHIME_LEVEL,
            envelope=synthio.Envelope(
                attack_time=0.3, decay_time=0.1, sustain_level=1, release_time=0.5
            ),
        )
        self.start = None

    def play(self):
        self.start = time.monotonic()
        self.note.frequency = 500
        self.synth.press(self.note)

    def update(self):
        """Returns False once finished"""
        elapsed = time.monotonic() - self.start
        if elapsed >= 1.5:
            self.synth.release(self.note)  # fades out over 0.5 s
            return False
        self.note.frequency = 500 * 2**elapsed  # up 1.5 octaves
        return True


class DoorCreak:
    """Plays on mixer voice 1, over the song on voice 0"""

    def __init__(self, mixer):
        self.voice = mixer.voice[1]
        self.voice.level = 1
        self.synth = synthio.Synthesizer(
            channel_count=MIXER_CHANNELS, sample_rate=MIXER_SAMPLE_RATE
        )
        # short pulses on the volume make the stick-slip "rasp" of a hinge;
        # the LFO's scale is the squeak's volume (0 = silent)
        self.rasp = synthio.LFO(
            waveform=CLICKS, rate=RASP[0], scale=0, interpolate=False
        )
        self.note = synthio.Note(frequency=PITCH[0], waveform=SAW, amplitude=self.rasp)
        self.synth.press(self.note)
        self.voice.play(self.synth)

        self.pitch = PITCH[0]  # where the squeak is gliding to
        self.level = 0
        self.last_glide = time.monotonic()

        self.chimes = tuple(
            chime(self.synth) for chime in (Doorbell, Boing, Laser, Frog, Saucer)
        )
        self.chime = None  # the chime now playing
        self.still_since = time.monotonic()
        self.chime_gap = random.uniform(*CHIME_GAP)

        self.gravity = None  # smoothed gravity direction
        self.last_gravity = None
        self.last_time = 0

    @property
    def squeaking(self):
        return self.level > 0 or self.rasp.scale > 0.01

    @property
    def playing(self):
        return self.squeaking or self.chime is not None

    def glide(self, now):
        """Ease pitch & volume toward their targets, so readings don't step"""
        step = 1 - math.exp(-(now - self.last_glide) / GLIDE)
        self.last_glide = now
        note = self.note
        note.frequency += step * (self.pitch - note.frequency)
        scale = self.rasp.scale + step * (self.level - self.rasp.scale)
        self.rasp.scale = scale if scale > 0.01 else self.level

    def update(self, x, y, z):
        """Call often with the accelerometer reading (in G)"""
        now = time.monotonic()
        self.glide(now)
        if self.chime and not self.chime.update():
            self.chime = None
        if self.gravity is None:
            self.gravity = [x, y, z]
            self.last_gravity = list(self.gravity)
            self.last_time = now
            return
        g = self.gravity
        for i, value in enumerate((x, y, z)):
            g[i] += SMOOTHING * (value - g[i])

        elapsed = now - self.last_time
        if elapsed < MEASURE_EVERY:
            return
        speed = math.degrees(angle_between(self.last_gravity, g)) / elapsed
        self.last_gravity = list(g)
        self.last_time = now

        if speed < QUIET_SPEED:
            self.level = 0
            if self.chime is None and now - self.still_since > self.chime_gap:
                self.chime = random.choice(self.chimes)
                self.chime.play()
                self.still_since = now
                self.chime_gap = random.uniform(*CHIME_GAP)
            return
        self.still_since = now
        angle = math.degrees(angle_between(CLOSED_GRAVITY, g))
        self.pitch = map_range(angle, 0, OPEN_ANGLE, *PITCH)
        self.rasp.rate = map_range(speed, QUIET_SPEED, LOUD_SPEED, *RASP)
        self.level = map_range(speed, QUIET_SPEED, LOUD_SPEED, *LEVEL)
        if verbose:
            print("Squeak: {:.0f} deg open, {:.0f} deg/s".format(angle, speed))


def angle_between(a, b):
    """Angle in radians between two 3D vectors"""
    dot = a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
    lengths = math.sqrt(
        (a[0] ** 2 + a[1] ** 2 + a[2] ** 2) * (b[0] ** 2 + b[1] ** 2 + b[2] ** 2)
    )
    if lengths == 0:
        return 0
    return math.acos(min(max(dot / lengths, -1), 1))
