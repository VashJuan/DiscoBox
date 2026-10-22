# SPDX-FileCopyrightText: 2026 John Cornelison for Vashon Software
# SPDX-License-Identifier: MIT

"""Test the door creak sound on its own: no song, accelerometer, lights or servo

To run: copy this file to the board as code.py (it runs instead of main.py).
Delete code.py from the board to go back to the normal show.

Plays pretend door swings of SWING seconds, quietest to loudest and back, as if
the door sped up then slowed down. Alternates two versions:
  A (1 beep first):  the creak as tuned in creak.py
  B (2 beeps first): higher, louder & less regular, to suit the transducer
"""

import array
import math
import random
import time

import board
from digitalio import DigitalInOut
import synthio

import sound
import creak

SWING = 3.5  # seconds
PAUSE = 2  # seconds of silence between swings

# Version B tuning, at slowest .. fastest swing
B_PITCH = (250, 600)  # Hz
B_RASP = (8, 25)  # clicks per second
B_LEVEL = (0.5, 1.0)
B_WOBBLE = 0.08  # random pitch & rasp change, 0..1
# wider pulses than version A: more sound in each click, so louder
B_CLICKS = array.array("h", [32767, 32767, 28000, 16000, 6000, 0])

# power the speaker amplifier
external_power = DigitalInOut(board.EXTERNAL_POWER)
external_power.switch_to_output(value=True)

audio, mixer = sound.setup_audio(test_clips=False)
beep = sound.make_sine_wave_sample(440, 0.5)
door = creak.DoorCreak(mixer)
a_rasp = door.rasp
b_rasp = synthio.LFO(waveform=B_CLICKS, rate=B_RASP[0], interpolate=False)


def beeps(count):
    for _ in range(count):
        mixer.voice[0].play(beep, loop=True)
        time.sleep(0.15)
        mixer.voice[0].stop()
        time.sleep(0.15)
    time.sleep(0.5)


def swing(pitch, rasp, level, wobble):
    start = time.monotonic()
    while (elapsed := time.monotonic() - start) < SWING:
        # 0 at the start & end of the swing, 1 in the middle
        speed = math.sin(math.pi * elapsed / SWING)
        jitter = 1 + random.uniform(-wobble, wobble)
        door.note.frequency = creak.map_range(speed, 0, 1, *pitch) * jitter
        door.note.amplitude.rate = creak.map_range(speed, 0, 1, *rasp) * jitter
        door.voice.level = creak.map_range(speed, 0, 1, *level)
        time.sleep(0.02)
    door.voice.level = 0
    time.sleep(PAUSE)


while True:
    print("A: creak.py tuning")
    beeps(1)
    door.note.amplitude = a_rasp
    swing(creak.PITCH, creak.RASP, (0.2, creak.MAX_LEVEL), 0)

    print("B: higher, louder, less regular")
    beeps(2)
    door.note.amplitude = b_rasp
    swing(B_PITCH, B_RASP, B_LEVEL, B_WOBBLE)
