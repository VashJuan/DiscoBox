# SPDX-FileCopyrightText: 2023 John Cornelison for Vashon Software
# SPDX-License-Identifier: MIT

"""Disco Mailbox - Using RP2040 Prop-Maker Feather"""
# https://www.adafruit.com/product/5768
# https://learn.adafruit.com/adafruit-rp2040-prop-maker-feather

# Modules in this folder:
#   config.py      settings (production, verbose, sound files, play_arpy)
#   sensors.py     VL53L1X distance sensor & LIS3DH accelerometer
#   lights.py      onboard status LED & external NeoPixel animations
#   prop_servo.py  servo sweep
#   sound.py       I2S audio, mixer & start-up audio tests
#   arp_synth.py   Arpy arpeggiator synth (when play_arpy is True)
#   arpy.py        Arpy arpeggio class

# TODO: https://learn.adafruit.com/
# keep-your-circuitpython-libraries-on-devices-up-to-date-with-circup/install-circup

import time

import board
from digitalio import DigitalInOut

from config import verbose, production, mp3files, play_arpy
import sound


def timing(label):
    """Seconds since power-up (time.monotonic() starts at boot)"""
    print("{:.2f} s: {}".format(time.monotonic(), label))


timing("main.py started")

#################################################
# provide power to the external components (speaker amp, NeoPixels, servo)
sleeping = True
external_power = DigitalInOut(board.EXTERNAL_POWER)
external_power.switch_to_output(value=not sleeping)

#################################################
# Music first: start a song before loading the (slow) animation libraries
audio, mixer = sound.setup_audio(test_clips=not production)
if not (production or play_arpy):
    sound.play_test_sounds(audio, mixer)

song_index = sound.first_song_index()
song_decoder = sound.open_song_decoder()
song = None
if not play_arpy:
    song = sound.play_song(audio, mixer, song_decoder, mp3files[song_index])
    sound.remember_next_song(song_index)
    timing("first song started")

import sensors  # pylint: disable=wrong-import-position
import lights  # pylint: disable=wrong-import-position
from prop_servo import ServoSweep  # pylint: disable=wrong-import-position

timing("libraries imported")

led = lights.setup_status_led()

#################################################
# region Enable rotary encoder (or other button/switch)
# https://www.adafruit.com/product/5740
# from adafruit_seesaw import seesaw, rotaryio, digitalio  # Adafruit ANO Rotary Encoder

# i2c = busio.I2C(board.SCL1, board.SDA1) # for QT Py RP2040
# i2c = board.I2C()  # uses board.SCL and board.SDA
i2c = board.STEMMA_I2C()  # Use built-in STEMMA QT connector on RP2040
# seesaw = seesaw.Seesaw(i2c, addr=0x49)
"""
seesaw_product = (seesaw.get_version() >> 16) & 0xFFFF
if verbose:
    print(f"Found product {seesaw_product}")
if seesaw_product != 5740:
    print("Wrong firmware loaded?  Expected 5740")

for i in range(1, 6):
    seesaw.pin_mode(i, seesaw.INPUT_PULLUP)

select = digitalio.DigitalIO(seesaw, 1)
up = digitalio.DigitalIO(seesaw, 2)
left = digitalio.DigitalIO(seesaw, 3)
down = digitalio.DigitalIO(seesaw, 4)
right = digitalio.DigitalIO(seesaw, 5)

encoder = rotaryio.IncrementalEncoder(seesaw)
last_position = None

buttons = [select, up, left, down, right]
button_names = ["Select", "Up", "Left", "Down", "Right"]
button_states = [False, False, False, False, False]
"""
# endregion

#################################################
# External button
"""
    switch = DigitalInOut(board.EXTERNAL_BUTTON)
    switch.direction = Direction.INPUT
    switch.pull = Pull.UP
    switch_state = False
"""

#################################################
# Set up the hardware
vl53 = sensors.setup_tof(i2c)
prop_servo = ServoSweep()
animations = lights.setup_animations()
lis3dh = sensors.setup_accelerometer()
timing("sensors, servo & lights set up")

if play_arpy:
    from arp_synth import setup_arpy, arp_step

    audio, mixer, arpy = setup_arpy(led)

# ################################################
loop_inner = 0
mailbox_lid_open = False
x = 0


def tick():
    """One pass of sensors, lights, servo & synth; runs while a song plays"""
    global loop_inner, x, mailbox_lid_open
    loop_inner += 1
    if verbose and (not loop_inner % 100):
        print("Inner Loop count: ", loop_inner)

    # -----------------
    # region Measure distance
    if vl53.data_ready and (not loop_inner % 25):
        if verbose:
            print("Distance: {} cm".format(vl53.distance))
        vl53.clear_interrupt()
    # endregion

    # -----------------
    # region Read LIS3DH values
    history = x
    x, y, z = sensors.read_acceleration(lis3dh)
    if x == 0:
        x = 0.000001
    rel_chg = ((x - history) / x) * 100
    # Gradient/slope/derivitive of recent values: are we de/accelorating?!
    # https://numpy.org/doc/stable/reference/generated/numpy.gradient.html
    # https://stackoverflow.com/a/24633888/6425926
    # https://www.stevenhirsch.ca/python-derivative/

    if verbose and lis3dh.tapped:
        print("Tapped!")
    # lis3dh.shake() averages readings over a 0.1 s sleep, which stalled the
    # animations; check the reading we already have instead (12 m/s^2 ~ 1.22 G)
    if verbose and (x * x + y * y + z * z) > 1.22**2:
        print("Shaken!")
    # endregion

    # Above code always runs
    # Code below only runs if mailbox lid is opened, to save battery
    """
    if not switch.value and switch_state is False:
        external_power.value = False
        switch_state = True
    if switch.value and switch_state is True:
        external_power.value = True
        switch_state = False
    """
    mailbox_lid_open = True

    external_power.switch_to_output(value=mailbox_lid_open)
    if mailbox_lid_open:
        # Mailbox is being used!!!

        # -----------------
        # region Check buttons/switches
        """
        position = encoder.position
        if position != last_position:
            last_position = position
            if verbose:
                print(f"Position: {position}")
        for b in range(5):
            if not buttons[b].value and button_states[b] is False:
                button_states[b] = True
                if verbose:
                    print(f"{button_names[b]} button pressed")
            if buttons[b].value and button_states[b] is True:
                button_states[b] = False
                if verbose:
                    print(f"{button_names[b]} button released")
        """
        # endregion

        if play_arpy:
            arp_step(arpy)

        # -----------------
        # modify audio based on switches?
        mixer.voice[0].level = 0.6

        # -----------------
        # Next step of the external neopixel animation
        # How to make responsive animations???
        # https://docs.circuitpython.org/projects/led-animation/en/latest/api.html#adafruit_led_animation.animation.Animation
        # https://learn.adafruit.com/cooperative-multitasking-in-circuitpython-with-asyncio?view=all
        animations.animate()

        # -----------------
        prop_servo.step()


while True:
    if play_arpy:  # the synth uses the audio output, so no songs
        tick()
        continue

    # This allows you to do other things while the audio plays!
    while song.playing:
        tick()
    song_index = (song_index + 1) % len(mp3files)
    song = sound.play_song(audio, mixer, song_decoder, mp3files[song_index])
    sound.remember_next_song(song_index)
