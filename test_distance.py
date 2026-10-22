# SPDX-FileCopyrightText: 2026 John Cornelison for Vashon Software
# SPDX-License-Identifier: MIT

"""Test the VL53L1X distance sensor on its own: no song, lights or servo

To run: copy this file to the board as code.py (it runs instead of main.py).
Delete code.py from the board to go back to the normal show.

1. A 1 s beep: proves the speaker & amplifier work.
2. Lists what is on the STEMMA QT (I2C) port; the VL53L1X is address 0x29.
3. Live: a tone whose pitch follows the distance, high when near, low when
   far, silent when nothing is in range. The serial console shows each reading.
"""

import time

import board
from digitalio import DigitalInOut
import synthio

import sound
import sensors
from creak import map_range

NEAR, FAR = 3, 130  # cm
PITCH = (1000, 200)  # Hz at NEAR, FAR

# power the speaker amplifier
external_power = DigitalInOut(board.EXTERNAL_POWER)
external_power.switch_to_output(value=True)

audio, mixer = sound.setup_audio(test_clips=False)

print("1. Beep")
mixer.voice[0].play(sound.make_sine_wave_sample(440, 0.5), loop=True)
time.sleep(1)
mixer.voice[0].stop()

print("2. I2C devices found:")
i2c = board.STEMMA_I2C()
while not i2c.try_lock():
    pass
print("  ", [hex(address) for address in i2c.scan()])
i2c.unlock()

vl53 = sensors.setup_tof(i2c)

synth = synthio.Synthesizer(
    channel_count=sound.MIXER_CHANNELS, sample_rate=sound.MIXER_SAMPLE_RATE
)
note = synthio.Note(frequency=PITCH[1])
synth.press(note)
mixer.voice[1].play(synth)
mixer.voice[1].level = 0

print("3. Live: move your hand toward and away from the sensor")
while True:
    if vl53.data_ready:
        distance = vl53.distance  # cm, or None when nothing is in range
        vl53.clear_interrupt()
        print("Distance:", distance, "cm")
        if distance is None:
            mixer.voice[1].level = 0
        else:
            note.frequency = map_range(distance, NEAR, FAR, *PITCH)
            mixer.voice[1].level = 0.6
    time.sleep(0.02)
