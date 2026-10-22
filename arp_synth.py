# SPDX-FileCopyrightText: 2023 John Cornelison for Vashon Software
# SPDX-License-Identifier: MIT

"""Arpeggio synth: Arpy (broken or rolling chord: notes of a chord individually &
quickly sounded in a progressive rising or descending order)"""

# https://github.com/todbot/circuitpython-synthio-tricks/tree/main/
# examples/eighties_arp based code

import time
from random import randrange

import board
import audiopwmio
import audiomixer
import synthio
import rainbowio
import ulab.numpy as np  # numerical approximation methods

from arpy import Arpy  # Uses arpeggios class

NUM_ARPY_VOICES = 3  # how many voices for each note
lpf_basef = 2500  # filter lowest frequency
lpf_resonance = 1.5  # filter q

# knobA = analogio.AnalogIn(board.A0)
# knobB = analogio.AnalogIn(board.A1)
# keys = keypad.Keys( (board.SDA, board.SCL), value_when_pressed=False )
analog_max = 65535  # Max knob value... 2**16-1
# https://docs.circuitpython.org/en/latest/shared-bindings/analogio/#analogio.AnalogIn
knobfilter = 0.75


# simple range mapper, like Arduino map()
def map_range(s, a1, a2, b1, b2):
    return b1 + ((s - a1) * (b2 - b1) / (a2 - a1))


def setup_arpy(led):
    """Start PWM audio and the arpeggiator; returns (audio, mixer, arpy)"""
    audio = audiopwmio.PWMAudioOut(board.RX)  # RX pin on QTPY RP2040

    mixer = audiomixer.Mixer(channel_count=1, sample_rate=28000, buffer_size=2048)
    synth = synthio.Synthesizer(channel_count=1, sample_rate=28000)
    audio.play(mixer)
    mixer.voice[0].play(synth)
    mixer.voice[0].level = 0.99

    # our oscillator waveform, a 512 sample downward saw wave going from +/-30k
    wave_saw = np.linspace(
        30000, -30000, num=512, dtype=np.int16
    )  # max is +/-32k but gives us headroom
    amp_env = synthio.Envelope(attack_level=1, sustain_level=1, release_time=0.5)

    voices = []  # holds our currently sounding voices ('Notes' in synthio speak)

    # called by arpy to turn on a note
    def note_on(n):
        print("  note on ", n)
        led.fill(rainbowio.colorwheel(n % 12 * 20))
        fo = synthio.midi_to_hz(n)
        voices.clear()  # delete any old voices
        for i in range(NUM_ARPY_VOICES):
            f = fo * (1 + i * 0.007)
            lpf_f = fo * 8  # a kind of key tracking
            lpf = synth.low_pass_filter(lpf_f, lpf_resonance)
            voices.append(
                synthio.Note(
                    frequency=f, filter=lpf, envelope=amp_env, waveform=wave_saw
                )
            )
        synth.press(voices)

    # called by arpy to turn off a note
    def note_off(n):
        print("  note off", n)
        led.fill(0)
        synth.release(voices)

    arpy = Arpy()
    arpy.note_on_handler = note_on
    arpy.note_off_handler = note_off
    arpy.on()

    arpy.root_note = 37
    arpy.set_arp("suspended4th")

    arpy.set_bpm(bpm=110, steps_per_beat=4)  # 110 bpm 16th notes
    arpy.set_transpose(distance=12, steps=0)
    return audio, mixer, arpy


def arp_step(arpy):
    """Simulate random key & knob input, then advance the arpeggiator"""
    key = randrange(4)
    print("Key simulation: ", key)
    if key == 0:
        arpy.next_arp()  # left button changes arp played
        print(arpy.arp_name())
    elif key == 1:
        steps = (arpy.trans_steps + 1) % 3  # right button changes arp up iterations
        print("steps", steps)
        arpy.set_transpose(steps=steps)
    elif key == 2:
        print("key 2...")
    elif key == 3:
        print("key 3...")

    # filter noisy adc
    knobA_value = randrange(analog_max)
    knobB_value = randrange(analog_max)
    knobA_value = knobA_value * knobfilter + (1 - knobfilter) * knobA_value
    knobB_value = knobB_value * knobfilter + (1 - knobfilter) * knobB_value

    # map knobA to root note
    arpy.root_note = int(map_range(knobA_value, 0, 65535, 24, 72))
    # map knobB to bpm
    arpy.set_bpm(map_range(knobB_value, 0, 65535, 40, 180))

    arpy.update()
    time.sleep(3)
