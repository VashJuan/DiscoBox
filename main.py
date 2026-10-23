# SPDX-FileCopyrightText: 2023 John Cornelison for Vashon Software
# SPDX-License-Identifier: MIT

"""Disco Mailbox - Using RP2040 Prop-Maker Feather"""
# https://www.adafruit.com/product/5768
# https://learn.adafruit.com/adafruit-rp2040-prop-maker-feather

# Modules in this folder:
#   config.py      settings (production, verbose, sound files, effects on/off)
#   sensors.py     VL53L1X distance sensor & LIS3DH accelerometer
#   lights.py      onboard status LED & external NeoPixel animations
#   prop_servo.py  servo sweep
#   sound.py       I2S audio, mixer & start-up audio tests
#   creak.py       cartoon door creak (when door_creak is True)
#   whistle.py     slide whistle from the distance sensor (when slide_whistle is True)
# The experimental arpeggiator lives apart, in arpy_mode/.

import time

import board
from digitalio import DigitalInOut

from config import verbose, production, mp3files, door_creak, slide_whistle
import sound


def timing(label):
    """Seconds since power-up (time.monotonic() starts at boot)"""
    print("{:.2f} s: {}".format(time.monotonic(), label))


timing("main.py started")

#################################################
# provide power to the external components (speaker amp, NeoPixels, servo)
external_power = DigitalInOut(board.EXTERNAL_POWER)
external_power.switch_to_output(value=True)

#################################################
# Music first: start a song before loading the (slow) animation libraries
audio, mixer = sound.setup_audio(test_clips=not production)
if not production:
    sound.play_test_sounds(audio, mixer)

song_index = sound.first_song_index()
song_decoder = sound.open_song_decoder()
song = sound.play_song(audio, mixer, song_decoder, mp3files[song_index])
sound.remember_next_song(song_index)
timing("first song started")

import sensors  # pylint: disable=wrong-import-position
import lights  # pylint: disable=wrong-import-position
from prop_servo import ServoSweep  # pylint: disable=wrong-import-position

timing("libraries imported")

#################################################
# Set up the hardware
i2c = board.STEMMA_I2C()  # Use built-in STEMMA QT connector on RP2040
vl53 = sensors.setup_tof(i2c)
prop_servo = ServoSweep()
animations = lights.setup_animations()
lis3dh = sensors.setup_accelerometer()
timing("sensors, servo & lights set up")

creak = None
if door_creak:
    from creak import DoorCreak

    creak = DoorCreak(mixer)

whistle = None
if slide_whistle:
    from whistle import SlideWhistle

    whistle = SlideWhistle(mixer)

ducker = sound.SongDucker(mixer)

# ################################################
loop_inner = 0


def tick():
    """One pass of sensors, lights & servo; runs while a song plays"""
    global loop_inner
    loop_inner += 1
    if verbose and (not loop_inner % 100):
        print("Inner Loop count: ", loop_inner)

    # -----------------
    # region Measure distance
    if vl53.data_ready:
        distance = vl53.distance  # cm, or None when nothing is in range
        vl53.clear_interrupt()
        if verbose and not loop_inner % 25:
            print("Distance: {} cm".format(distance))
        if whistle:
            whistle.distance(distance)
    if whistle:
        whistle.update()
    # endregion

    # -----------------
    # region Read LIS3DH values
    x, y, z = sensors.read_acceleration(lis3dh)
    if verbose and lis3dh.tapped:
        print("Tapped!")
    # lis3dh.shake() averages readings over a 0.1 s sleep, which stalled the
    # animations; check the reading we already have instead (12 m/s^2 ~ 1.22 G)
    if verbose and (x * x + y * y + z * z) > 1.22**2:
        print("Shaken!")
    if creak:
        creak.update(x, y, z)
    # endregion

    # Turn the song down while an effect plays
    ducker.update(
        (creak is not None and creak.voice.level > 0)
        or (whistle is not None and whistle.playing)
    )

    # -----------------
    # Next step of the external neopixel animation
    # How to make responsive animations???
    # https://docs.circuitpython.org/projects/led-animation/en/latest/api.html#adafruit_led_animation.animation.Animation
    # https://learn.adafruit.com/cooperative-multitasking-in-circuitpython-with-asyncio?view=all
    animations.animate()

    # -----------------
    prop_servo.step()


while True:
    # This allows you to do other things while the audio plays!
    while song.playing:
        tick()
    song_index = (song_index + 1) % len(mp3files)
    song = sound.play_song(audio, mixer, song_decoder, mp3files[song_index])
    sound.remember_next_song(song_index)
