# SPDX-FileCopyrightText: 2026 John Cornelison for Vashon Software
# SPDX-License-Identifier: MIT

"""Try door sounds that might replace the creak: no accelerometer, lights or servo

To run: copy this file to the board as code.py (it runs instead of main.py).
Delete code.py from the board to go back to the normal show.

Plays each sound in turn over a song turned down as the show ducks it, so they
can be judged outdoors against the music. All are synthesized (no sound files)
and sit above ~300 Hz, where the transducer is loud. Beeps first tell which:
  1 beep:  squeak   - a high hinge "eeek", rising
  2 beeps: doorbell - "ding-dong"
  3 beeps: boing    - cartoon spring
  4 beeps: ta-da    - quick fanfare
  5 beeps: cuckoo   - cuckoo clock call
"""

import array
import math
import time

import board
from digitalio import DigitalInOut
import synthio

import sound
from config import mp3files

WITH_SONG = True  # False to hear the sounds on their own
LEVEL = 0.8  # mixer volume of the sounds
PAUSE = 3  # seconds between sounds


def wave(shape):
    """64-sample waveform from shape(phase 0..1) -> -1..1"""
    return array.array("h", [int(30000 * shape(i / 64)) for i in range(64)])


SINE = wave(lambda p: math.sin(2 * math.pi * p))
TRIANGLE = wave(lambda p: 1 - 4 * abs(p - 0.5))
SQUARE = wave(lambda p: 1 if p < 0.5 else -1)
SAW = wave(lambda p: 1 - 2 * p)
# a few harmonics, for a brighter bell than a pure sine
BELL = wave(
    lambda p: (
        math.sin(2 * math.pi * p)
        + 0.5 * math.sin(4 * math.pi * p)
        + 0.25 * math.sin(6 * math.pi * p)
    ) / 1.75
)
RAMP_UP = array.array("h", [0, 32767])  # LFO shape: 0 to 1 once

# power the speaker amplifier
external_power = DigitalInOut(board.EXTERNAL_POWER)
external_power.switch_to_output(value=True)

audio, mixer = sound.setup_audio(test_clips=False)
synth = synthio.Synthesizer(
    channel_count=sound.MIXER_CHANNELS, sample_rate=sound.MIXER_SAMPLE_RATE
)
mixer.voice[1].play(synth)
mixer.voice[1].level = LEVEL
beep = sound.make_sine_wave_sample(440, 0.5)
song = None
decoder = sound.open_song_decoder() if WITH_SONG else None


def keep_song_playing():
    global song
    if WITH_SONG and (song is None or not song.playing):
        song = sound.play_song(audio, mixer, decoder, mp3files[0])
        mixer.voice[0].level = sound.DUCKED_LEVEL


def beeps(count):
    for _ in range(count):
        mixer.voice[2].play(beep, loop=True)
        time.sleep(0.15)
        mixer.voice[2].stop()
        time.sleep(0.15)
    time.sleep(0.5)


def play(note, seconds):
    synth.press(note)
    time.sleep(seconds)
    synth.release(note)


def squeak():
    # rasp clicks like the creak, but up where the transducer is loud
    clicks = array.array("h", [32767, 20000, 0, 0, 0, 0])
    note = synthio.Note(
        frequency=700,
        waveform=SAW,
        amplitude=synthio.LFO(waveform=clicks, rate=22, interpolate=False),
        bend=synthio.LFO(waveform=RAMP_UP, rate=1 / 0.7, scale=0.8, once=True),
    )
    play(note, 0.7)


def doorbell():
    ring = synthio.Envelope(
        attack_time=0.005, decay_time=1.2, sustain_level=0, release_time=0.3
    )
    ding = synthio.Note(frequency=659, waveform=BELL, envelope=ring)  # E5
    dong = synthio.Note(frequency=523, waveform=BELL, envelope=ring)  # C5
    synth.press(ding)
    time.sleep(0.5)
    synth.press(dong)
    time.sleep(1.5)
    synth.release_all()


def boing():
    wobble = synthio.LFO(rate=14, scale=0.2)  # octaves
    note = synthio.Note(
        frequency=392,
        waveform=TRIANGLE,
        bend=wobble,
        envelope=synthio.Envelope(
            attack_time=0.005, decay_time=1.0, sustain_level=0, release_time=0.1
        ),
    )
    synth.press(note)
    start = time.monotonic()
    while (elapsed := time.monotonic() - start) < 1.0:
        wobble.scale = 0.2 * (1 - elapsed)  # the spring settles
        time.sleep(0.02)
    synth.release(note)


def ta_da():
    for frequency in (523, 659, 784):  # C5 E5 G5
        play(synthio.Note(frequency=frequency, waveform=SQUARE), 0.09)
    play(
        synthio.Note(
            frequency=1047,  # C6
            waveform=SQUARE,
            envelope=synthio.Envelope(
                attack_time=0.01, decay_time=0.6, sustain_level=0.3,
                release_time=0.2,
            ),
        ),
        0.7,
    )


def cuckoo():
    for _ in range(2):
        play(synthio.Note(frequency=784, waveform=TRIANGLE), 0.22)  # G5
        time.sleep(0.05)
        play(synthio.Note(frequency=622, waveform=TRIANGLE), 0.35)  # E flat 5
        time.sleep(0.3)


SOUNDS = [squeak, doorbell, boing, ta_da, cuckoo]

while True:
    for number, effect in enumerate(SOUNDS, 1):
        keep_song_playing()
        print(number, effect.__name__)
        beeps(number)
        effect()
        time.sleep(PAUSE)
