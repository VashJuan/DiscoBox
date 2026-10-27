# SPDX-FileCopyrightText: 2026 John Cornelison for Vashon Software
# SPDX-License-Identifier: MIT

"""Door sounds: a hinge squeak while the door swings, a doorbell or boing when still

The Feather is mounted on the door, so the accelerometer sees the direction of
gravity turn as the door swings.
- Squeak: plays while the door moves. Its pitch follows the door's angle, high
  when closed (up) and low when open (down), so it rises as the door goes up and
  falls as it comes down. The faster the swing, the louder and raspier.
- Chimes: while the door stays still, every 30-50 seconds one of the theme's
  chimes (CHIMES in themes/*.py): a doorbell "ding-dong", a cartoon "boing", a
  laser "pew pew pew", a frog "ribbit", a flying saucer; for Halloween a ghost,
  a wolf howl, bats, a spooky organ, or a recorded WAV (evil laugh, cries).
"""

import array
import math
import random
import time

import audiocore
import synthio

from config import verbose, sound_dir, theme_settings
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

# Squeak (pitch & rasp come from the theme)
PITCH = theme_settings.SQUEAK_PITCH  # Hz, door closed .. fully open
RASP = theme_settings.SQUEAK_RASP  # clicks per second, slow .. fast swing
LEVEL = (0.2, 0.9)  # volume, slow .. fast swing
GLIDE = 0.15  # seconds for pitch & volume to settle on a new reading

# Chimes while the door is still
CHIME_GAP = (30, 50)  # seconds of stillness before each chime
CHIME_LEVEL = 0.8
RECORDING_LEVEL = 1.0  # mixer volume of recorded (WAV) chimes


def map_range(s, a1, a2, b1, b2):
    """Like Arduino map(), but clamped to b1..b2"""
    s = min(max(s, a1), a2)
    return b1 + ((s - a1) * (b2 - b1) / (a2 - a1))


def wave(shape):
    """64-sample waveform from shape(phase 0..1) -> -1..1"""
    return array.array("h", [int(30000 * shape(i / 64)) for i in range(64)])


SAW = wave(lambda p: 1 - 2 * p)  # bright & buzzy
TRIANGLE = wave(lambda p: 1 - 4 * abs(p - 0.5))
SINE = wave(lambda p: math.sin(2 * math.pi * p))
# a sine with a little 3rd harmonic: a hollow "oooh"
HOLLOW = wave(
    lambda p: (math.sin(2 * math.pi * p) + 0.3 * math.sin(6 * math.pi * p)) / 1.3
)
# pipe organ: a few drawbar-like harmonics
ORGAN = wave(
    lambda p: (
        math.sin(2 * math.pi * p)
        + 0.6 * math.sin(4 * math.pi * p)
        + 0.3 * math.sin(6 * math.pi * p)
        + 0.2 * math.sin(8 * math.pi * p)
    ) / 2.1
)
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


def glide_through(points, elapsed):
    """Hz at elapsed seconds along points ((seconds, Hz), ...)"""
    for (t1, hz1), (t2, hz2) in zip(points, points[1:]):
        if elapsed < t2:
            # glide evenly in pitch (octaves), not in Hz
            return hz1 * (hz2 / hz1) ** ((elapsed - t1) / (t2 - t1))
    return points[-1][1]


class Glide:
    """One note gliding through PATH ((seconds, Hz), ...), with a wobble"""

    WAVE = SINE
    PATH = ((0, 440), (1, 440))
    WOBBLE = (5, 0.03)  # rate (Hz) & depth (octaves)
    ENVELOPE = (0.2, 0.4)  # attack & release, seconds

    def __init__(self, synth):
        self.synth = synth
        self.note = synthio.Note(
            frequency=self.PATH[0][1],
            waveform=self.WAVE,
            bend=synthio.LFO(rate=self.WOBBLE[0], scale=self.WOBBLE[1]),
            amplitude=CHIME_LEVEL,
            envelope=synthio.Envelope(
                attack_time=self.ENVELOPE[0],
                decay_time=0.1,
                sustain_level=1,
                release_time=self.ENVELOPE[1],
            ),
        )
        self.start = None

    def play(self):
        self.start = time.monotonic()
        self.note.frequency = self.PATH[0][1]
        self.synth.press(self.note)

    def update(self):
        """Returns False once finished"""
        elapsed = time.monotonic() - self.start
        if elapsed >= self.PATH[-1][0]:
            self.synth.release(self.note)  # fades over the release time
            return False
        self.note.frequency = glide_through(self.PATH, elapsed)
        return True


class Ghost(Glide):
    """Ghost: a hollow "woooOOOooo" that swells and sinks"""

    WAVE = HOLLOW
    PATH = ((0, 450), (1.0, 700), (2.4, 380))
    WOBBLE = (4.5, 0.04)
    ENVELOPE = (0.5, 0.7)


class Howl(Glide):
    """Wolf howl: slides up, holds with a wobble, falls away"""

    WAVE = TRIANGLE
    PATH = ((0, 480), (0.5, 1000), (1.5, 950), (2.3, 650))
    WOBBLE = (6, 0.025)
    ENVELOPE = (0.15, 0.5)


class Bats(Repeats):
    """Bats: quick high chirps"""

    COUNT = 6
    EVERY = 0.09
    TAIL = 0.2

    def make_note(self):
        return synthio.Note(
            frequency=random.uniform(3200, 4200),
            waveform=TRIANGLE,
            amplitude=CHIME_LEVEL,
            bend=synthio.LFO(waveform=RAMP_UP, rate=1 / 0.05, scale=-0.6, once=True),
            envelope=synthio.Envelope(
                attack_time=0.002, decay_time=0.05, sustain_level=0, release_time=0.02
            ),
        )


class Organ:
    """Spooky organ: the opening of Bach's Toccata in D minor, ending on a chord"""

    # (Hz, start, seconds)
    SCORE = (
        (880, 0, 0.12),  # A5
        (784, 0.12, 0.08),  # G5
        (880, 0.2, 0.6),  # A5
        (784, 0.9, 0.12),  # G5
        (698, 1.02, 0.12),  # F5
        (659, 1.14, 0.12),  # E5
        (587, 1.26, 0.12),  # D5
        (554, 1.38, 0.3),  # C sharp 5
        (587, 1.7, 1.3),  # D minor chord: D5,
        (698, 1.7, 1.3),  # F5,
        (880, 1.7, 1.3),  # A5
    )
    LENGTH = 3.0  # seconds, the last notes' end

    def __init__(self, synth):
        self.synth = synth
        envelope = synthio.Envelope(
            attack_time=0.01, decay_time=0.1, sustain_level=0.9, release_time=0.15
        )
        self.notes = [
            synthio.Note(
                frequency=hz,
                waveform=ORGAN,
                envelope=envelope,
                amplitude=CHIME_LEVEL * 0.45,  # up to 3 at once
            )
            for hz, _, _ in self.SCORE
        ]
        self.start = None

    def play(self):
        self.start = time.monotonic()
        self.update()

    def update(self):
        """Returns False once finished"""
        elapsed = time.monotonic() - self.start
        for note, (_, start, length) in zip(self.notes, self.SCORE):
            if elapsed >= start + length:
                self.synth.release(note)
            elif elapsed >= start and note not in self.synth.pressed:
                self.synth.press(note)
        return elapsed < self.LENGTH


class Recording:
    """A recorded chime: a WAV file played on mixer voice 3"""

    def __init__(self, voice, path):
        self.voice = voice
        self.path = path
        self.file = None

    def play(self):
        self.file = open(self.path, "rb")
        self.voice.level = RECORDING_LEVEL
        self.voice.play(audiocore.WaveFile(self.file))

    def update(self):
        """Returns False once finished"""
        if self.voice.playing:
            return True
        self.file.close()
        return False


# Chime names for the themes' CHIMES
CHIMES = {
    "doorbell": Doorbell,
    "boing": Boing,
    "laser": Laser,
    "frog": Frog,
    "saucer": Saucer,
    "ghost": Ghost,
    "howl": Howl,
    "bats": Bats,
    "organ": Organ,
}


def make_chimes(synth, voice):
    """The theme's chimes; WAV files missing from sounds/ are left out"""
    chimes = []
    for name in theme_settings.CHIMES:
        if not name.endswith(".wav"):
            chimes.append(CHIMES[name](synth))
            continue
        try:
            open(sound_dir + name, "rb").close()
        except OSError:
            if verbose:
                print("No", sound_dir + name, "- chime left out")
            continue
        chimes.append(Recording(voice, sound_dir + name))
    return chimes


class DoorCreak:
    """Plays on mixer voice 1 (recorded chimes on voice 3), over the song on voice 0

    on_chime, if given, is called as each chime starts (e.g. to flash the lights).
    """

    def __init__(self, mixer, on_chime=None):
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

        self.chimes = make_chimes(self.synth, mixer.voice[3])
        self.on_chime = on_chime
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
            if (
                self.chimes
                and self.chime is None
                and now - self.still_since > self.chime_gap
            ):
                self.chime = random.choice(self.chimes)
                self.chime.play()
                if self.on_chime:
                    self.on_chime()
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
