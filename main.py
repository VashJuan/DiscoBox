# SPDX-FileCopyrightText: 2023 John Cornelison for Vashon Software
# SPDX-License-Identifier: MIT

"""Disco Mailbox - Using RP2040 Prop-Maker Feather"""
# https://www.adafruit.com/product/5768
# https://learn.adafruit.com/adafruit-rp2040-prop-maker-feather

# region Libraries
# TODO: https://learn.adafruit.com/keep-your-circuitpython-libraries-on-devices-up-to-date-with-circup/install-circup

import time, board  # , analogio, keypad
import array, math
import ulab.numpy as np  # numerical approximation methods
from random import randrange
import asyncio

# import adafruit_ticks

from audiocore import RawSample
import audiocore  # for WAV files
import audiobusio  # for I2S audio with external I2S DAC board
import audiomixer
import pwmio, audiopwmio, synthio, simpleio, audiomp3

# from audiomp3 import MP3Decoder

# import digitalio
from digitalio import DigitalInOut, Pull
from arpy import Arpy  # Uses arpeggios class:

try:
    from audioio import AudioOut
except ImportError:
    try:
        from audiopwmio import PWMAudioOut as AudioOut
    except ImportError:
        print("Input error")
        pass  # not always supported by every board!

import adafruit_vl53l1x  # "Time of flight", i.e., distance sensor
import adafruit_lis3dh  # accelerometer

# from adafruit_seesaw import seesaw, rotaryio, digitalio  # Adafruit ANO Rotary Encoder
from adafruit_motor import servo


# https://learn.adafruit.com/circuitpython-led-animations
import neopixel, rainbowio
from adafruit_led_animation.animation.rainbow import Rainbow
from adafruit_led_animation.animation.comet import Comet
from adafruit_led_animation.animation.rainbowcomet import RainbowComet
from adafruit_led_animation.animation.rainbowchase import RainbowChase
from adafruit_led_animation.animation.rainbowsparkle import RainbowSparkle
from adafruit_led_animation.animation.chase import Chase
from adafruit_led_animation.animation.rainbow import Rainbow
from adafruit_led_animation.sequence import AnimationSequence
from adafruit_led_animation import helper

# from adafruit_led_animation.color import PURPLE, JADE, AMBER
import adafruit_led_animation.color as color  # now we can use color.RED, etc.

"""
Colors defined by Adafruit Led Animation library:
    https://docs.circuitpython.org/projects/led-animation/en/latest/api.html#adafruit-led-animation-color
    Amber, Aqua, Black, Blue, Cyan, Gold, Green, Jade, Magenta, Old lace, Orange, Pink, Purple, Red, Teal, White, Yellow

    Old lace = warm white
    Black = off
    RAINBOW is a list of colors to use for cycling through Includes, in order: red, orange, yellow, green, blue, and purple
    RGBW_WHITE_RGB is for RGBW strips to illuminate only the RGB diodes
    RGBW_WHITE_RGBW is for RGBW strips to illuminate the RGB and White diodes
    RGBW_WHITE_W is for RGBW strips to illuminate only White diode
"""

# Python modules:
# from another_file import another_function
# import another_file
# from another_file import *

# endregion

sound_dir = "sounds/"
mp3files = [
    "ClassicalGas.mp3",
    "happy.mp3",
    "fire.mp3",
    "slow.mp3",
    "Africa.mp3",
    "oneday.mp3",
]
verbose = True  # print out debug information to serial port?
# verbose = False   # print out debug information to serial port?

################################################
# region Arpeggio: Arpy (broken or rolling chord: notes of a chord individually &
# quickly sounded in a progressive rising or descending order)
NUM_ARPY_VOICES = 3  # how many voices for each note
lpf_basef = 2500  # filter lowest frequency
lpf_resonance = 1.5  # filter q

# knobA = analogio.AnalogIn(board.A0)
# knobB = analogio.AnalogIn(board.A1)
# keys = keypad.Keys( (board.SDA, board.SCL), value_when_pressed=False )
analog_max = 65535  # Max knob value... 2**16-1
# https://docs.circuitpython.org/en/latest/shared-bindings/analogio/#analogio.AnalogIn
led = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.1)
# endregion

#################################################
# provide power to the external components
sleeping = True
external_power = DigitalInOut(board.EXTERNAL_POWER)
external_power.switch_to_output(value=not sleeping)
# external_power.direction = Direction.OUTPUT
# external_power.value = True


#################################################
# region Enable rotary encoder (or other button/switch)
# https://www.adafruit.com/product/5740

# i2c = busio.I2C(board.SCL1, board.SDA1) # for QT Py RP2040
# i2c = board.I2C()  # uses board.SCL and board.SDA
i2c = board.STEMMA_I2C()  # Use built-in STEMMA QT connector on RP2040
# seesaw = seesaw.Seesaw(i2c, addr=0x49)
# endregion


"""
seesaw_product = (seesaw.get_version() >> 16) & 0xFFFF
if verbose:
    print(f"Found product {seesaw_product}")
if seesaw_product != 5740:
    print("Wrong firmware loaded?  Expected 5740")

for i in range(1, 6):
    seesaw.pin_mode(i, seesaw.INPUT_PULLUP)

select = digitalio.DigitalIO(seesaw, 1)
select_held = False
up = digitalio.DigitalIO(seesaw, 2)
up_held = False
left = digitalio.DigitalIO(seesaw, 3)
left_held = False
down = digitalio.DigitalIO(seesaw, 4)
down_held = False
right = digitalio.DigitalIO(seesaw, 5)
right_held = False

encoder = rotaryio.IncrementalEncoder(seesaw)
last_position = None

buttons = [select, up, left, down, right]
button_names = ["Select", "Up", "Left", "Down", "Right"]
button_states = [select_held, up_held, left_held, down_held, right_held]
"""

#################################################
# External button
"""
    switch = DigitalInOut(board.EXTERNAL_BUTTON)
    switch.direction = Direction.INPUT
    switch.pull = Pull.UP
    switch_state = False
    or
    external_button = digitalio.DigitalInOut(board.A1)
    external_button.switch_to_input(pull=digitalio.Pull.UP)
"""


#################################################
# region Time of Flight - i.e., distance measurement
# https://learn.adafruit.com/adafruit-vl53l1x
vl53 = adafruit_vl53l1x.VL53L1X(i2c)
vl53.distance_mode = 1
vl53.timing_budget = 100

if verbose:
    print("VL53L1X Simple Test.")
    print("--------------------")
    model_id, module_type, mask_rev = vl53.model_info
    print("Model ID: 0x{:0X}".format(model_id))
    print("Module Type: 0x{:0X}".format(module_type))
    print("Mask Revision: 0x{:0X}".format(mask_rev))
    print("Distance Mode: ", end="")
    if vl53.distance_mode == 1:
        print("SHORT mode")
    elif vl53.distance_mode == 2:
        print("LONG mode")
    else:
        print("UNKNOWN mode")
    print("Timing Budget: {}".format(vl53.timing_budget))
    print("--------------------")

vl53.start_ranging()
# endregion

#################################################
# region Enable servo motor
pwm = pwmio.PWMOut(board.EXTERNAL_SERVO, duty_cycle=2**15, frequency=50)
prop_servo = servo.Servo(pwm)
angle = 0
angle_plus = True
# endregion

#################################################
# region External neopixels
# https://learn.adafruit.com/circuitpython-led-animations
# https://learn.adafruit.com/adafruit-neopixel-uberguide
# https://learn.adafruit.com/adafruit-neopixel-uberguide/neomatrix-library
# TODO: http://fastled.io/
# TODO: https://learn.adafruit.com/adafruit-neopixel-uberguide/advanced-coding
num_pixels = 64
anim_speed = 0.1
pixels = neopixel.NeoPixel(
    board.EXTERNAL_NEOPIXELS, num_pixels, brightness=0.05, auto_write=False
)

pixel_wing_vertical = helper.PixelMap.vertical_lines(
    pixels, 8, 8, helper.horizontal_strip_gridmap(8, alternating=False)
)
pixel_wing_horizontal = helper.PixelMap.horizontal_lines(
    pixels, 8, 8, helper.horizontal_strip_gridmap(8, alternating=False)
)
comet_h = Comet(
    pixel_wing_horizontal,
    speed=anim_speed,
    color=color.PURPLE,
    tail_length=7,
    bounce=True,
)
comet_v = Comet(
    pixel_wing_vertical, speed=anim_speed, color=color.AMBER, tail_length=6, bounce=True
)
chase_h = Chase(
    pixel_wing_horizontal, speed=anim_speed, size=7, spacing=6, color=color.JADE
)
rainbow_chase_v = RainbowChase(
    pixel_wing_vertical, speed=anim_speed, size=7, spacing=2, step=8
)
rainbow_comet_v = RainbowComet(
    pixel_wing_vertical, speed=anim_speed, tail_length=7, bounce=True
)
rainbow_v = Rainbow(pixel_wing_vertical, speed=anim_speed, period=2)
# rainbow_chase_h = RainbowChase(pixel_wing_horizontal, speed=anim_speed, size=3, spacing=3)
rainbow_chase_h = RainbowChase(pixels, speed=anim_speed, size=3, spacing=3)
rainbow_sparkle = RainbowSparkle(pixels, speed=anim_speed, num_sparkles=10)

# Customize animation sequence/effects
animations = AnimationSequence(
    rainbow_v,
    #    comet_h,
    rainbow_comet_v,
    #    chase_h,
    rainbow_chase_v,
    #    comet_v,
    rainbow_chase_h,
    rainbow_sparkle,
    advance_interval=5,
    random_order=True,
)
# endregion

#################################################
# region Onboard i2c LIS3DH accelerometer
# https://learn.adafruit.com/adafruit-lis3dh-triple-axis-accelerometer-breakout
i2c = board.I2C()
int1 = DigitalInOut(board.ACCELEROMETER_INTERRUPT)
lis3dh = adafruit_lis3dh.LIS3DH_I2C(i2c, int1=int1)
# https://learn.adafruit.com/adafruit-lis3dh-triple-axis-accelerometer-breakout/arduino#accelerometer-ranges-1729247
lis3dh.range = adafruit_lis3dh.RANGE_2_G
# https://learn.adafruit.com/adafruit-lis3dh-triple-axis-accelerometer-breakout/arduino#tap-and-double-tap-detection-1729254
lis3dh.set_tap(1, 100)  # set_tap(2, THRESHOLD) looks for double taps
# endregion

#################################################
# region Music & Audio...
# https://github.com/todbot/circuitpython-tricks#audio

# i2s audio playback on PropMaker Feather RP2040
audio = audiobusio.I2SOut(
    board.I2S_BIT_CLOCK, board.I2S_WORD_SELECT, board.I2S_DATA
)  # aka DAC!
# audio = audioio.AudioOut(board.RX) # Used on boards without I2S audio
# dac = audioio.AudioOut(board.SPEAKER)


# Using mixer just to enable volume control
# channel1 is mp3, channel 2 will be used for synth sounds
# https://learn.adafruit.com/adafruit-rp2040-prop-maker-feather/audio-mixer-volume-control
mixer = audiomixer.Mixer(
    voice_count=2,
    channel_count=1,
    sample_rate=22050,  # 8000,
    #    buffer_size=2048,
    bits_per_sample=16,
    samples_signed=True,  # False,
)
# mixer = audiomixer.Mixer(channel_count=2, sample_rate=22050, buffer_size=2048)
audio.play(mixer)  #   , loop=True # attach mixer to audio playback
# time.sleep(1)
# audio.stop()

wav_file2 = "sounds/amenfull_22k_s16.wav"  # in 'circuitpython-tricks/larger-tricks/breakbeat_wavs'
mp3_file2 = (
    "sounds/One_Day-22Hz-16kbpsConst.mp3"  # in 'circuitpython-tricks/larger-tricks/wav'
)
# https://freesound.org/people/f-r-a-g-i-l-e/sounds/476663/

wave = audiocore.WaveFile(open(wav_file2, "rb"))
mp3 = audiomp3.MP3Decoder(open(mp3_file2, "rb"))
mixer.voice[0].play(wave)
mixer.voice[0].level = 0.4
mixer.voice[1].play(mp3)
mixer.voice[1].level = 0.2

play_arpy = False

if True:
    for f in (262, 294, 330, 349, 392, 440, 494, 523):
        if verbose:
            print("play ", f, " MHz tone...")
        # simpleio.tone(board.SPEAKER, f, 0.25)
        time.sleep(0.5)

    # ######## Get MP3 file
    # https://github.com/todbot/circuitpython-tricks#playing-mp3-files
    # You have to specify some mp3 file when creating the decoder
    mp3_file = open(sound_dir + mp3files[0], "rb")
    mp3_stream = audiomp3.MP3Decoder(mp3_file)  # Create object only once to save memory
    if verbose:
        bps = mp3_stream.bits_per_sample  # 16
        sr = mp3_stream.sample_rate  # 44100
        print("mp3_stream bps:", bps, " sample rate:", sr)

    # ####### Get WAV file
    # https://github.com/todbot/circuitpython-tricks#preparing-audio-files-for-circuitpython
    # mixer = audiomixer.Mixer(voice_count=1, sample_rate=16000, channel_count=1,
    #                       bits_per_sample=16, samples_signed=True)
    # Play a WAV file (e.g., from https://github.com/KristofferKarlAxelEkstrand/AKWF-FREE, https://WaveEditOnline.com)
    wav_song = audiocore.WaveFile(open(sound_dir + "bowing.wav", "rb"))  # 16 & 44100
    if verbose:
        bps = wav_song.bits_per_sample  # 16
        sr = wav_song.sample_rate  # 44100
        print("WAV song bps:", bps, " sample rate:", sr)

    ######## Play Midi
    # https://github.com/todbot/circuitpython-tricks#usb-midi
    # https://docs.circuitpython.org/en/latest/shared-bindings/synthio/index.html#synthio.MidiTrack
    melody = synthio.MidiTrack(
        b"\0\x90H\0*\x80H\0\6\x90J\0*\x80J\0\6\x90L\0*\x80L\0\6\x90J\0"
        + b"*\x80J\0\6\x90H\0*\x80H\0\6\x90J\0*\x80J\0\6\x90L\0T\x80L\0"
        + b"\x0c\x90H\0T\x80H\0\x0c\x90H\0T\x80H\0",
        tempo=640,
    )
    if verbose:
        bps = "undefined"  # melody.bits_per_sample
        sr = melody.sample_rate  # 11025
        print("midi melody bps:", bps, " sample rate:", sr)
        print("play midi melody")
        audio.play(melody)
        while audio.playing:
            pass
        print("play midi melody DONE")

    ##### Get Midi file
    # https://bitmidi.com/, https://midisfree.com, https://musiclab.chromeexperiments.com/Song-Maker/,

    # data = open(sound_dir + "lonely.mid", "rb")
    # midi = synthio.from_file(data)
    if False:  # verbose:
        bps = "undefined"  # midi.bits_per_sample
        sr = midi.sample_rate  # 11025
        print("midi file bps:", bps, " sample rate:", sr)
        print("Play midi file")
        audio.play(midi)  # mixer needs samples_signed=True
        while audio.playing:
            pass
        print("Play midi file DONE")

    ######## Create Synth
    # synth = synthio.Synthesizer(channel_count=1, sample_rate=22050)
    synth = synthio.Synthesizer(channel_count=1, sample_rate=9990)
    if verbose:
        bps = "undefined"  # synth.bits_per_sample
        sr = synth.sample_rate  # 9990
        print("Synth sample bps:", bps, " sample rate:", sr)

    ####### Create sine wave sample
    # https://github.com/todbot/circuitpython-tricks#making-simple-tones
    tone_volume = 0.1  # Increase this to increase the volume of the tone.
    frequency = 440  # Set this to the Hz of the tone you want to generate.
    length = 1000 // frequency
    sine_wave = array.array("H", [0] * length)
    for i in range(length):
        sine_wave[i] = int(
            (1 + math.sin(math.pi * 2 * i / length)) * tone_volume * (2**15 - 1)
        )
    sine_wave_sample = RawSample(sine_wave)
    if verbose:
        bps = "undefined"  # sine_wave_sample.bits_per_sample
        sr = sine_wave_sample.sample_rate  # 8000
        print("sine_wave_sample sample bps:", bps, " sample rate:", sr)
        # mixer.music.load('background.wav')
        # mixer.music.play(-1)  # will cause song to loop

    ########## Play some of the above...
    if False:
        # audio.play(mixer)

        """
        mixer.voice[0].play(synth)  # requires mixer samples_signed=True
        mixer.voice[0].level = 0.4
        if verbose: print("Mixer voice 0 playing...")
        time.sleep(1)
        """

        # audio.play(sine_wave_sample, loop=True)
        print("sine_wavesample rate: ", sine_wave_sample.sample_rate)  # 8000

        mixer.voice[1].play(
            sine_wave_sample
        )  # requires signed_samples=False ... The sample's sample rate does not match the mixer's
        mixer.voice[1].level = 0.4
        if verbose:
            print("Mixer voice 1 playing...")
        time.sleep(1)


elif play_arpy:
    # https://github.com/todbot/circuitpython-synthio-tricks/tree/main/examples/eighties_arp based code
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

    # simple range mapper, like Arduino map()
    def map_range(s, a1, a2, b1, b2):
        return b1 + ((s - a1) * (b2 - b1) / (a2 - a1))

    arpy = Arpy()
    arpy.note_on_handler = note_on
    arpy.note_off_handler = note_off
    arpy.on()

    arpy.root_note = 37
    arpy.set_arp("suspended4th")

    arpy.set_bpm(bpm=110, steps_per_beat=4)  # 110 bpm 16th notes
    arpy.set_transpose(distance=12, steps=0)

    knobfilter = 0.75
    knobA_value = 10000  # knobA.value
    knobB_value = 10000  # knobB.value

else:
    # synthio_eighties_dystopia.py based code...
    print("no op")

knobfilter = 0.75
knobA_value = 10000  # knobA.value
knobB_value = 10000  # knobB.value
# endregion

#################################################
loop = 0
loop_inner = 0
mailbox_lid_open = False
history = [0, 0, 0, 0, 0]

while True:
    loop += 1
    if verbose and (not loop % 100):
        print("Loop count: ", loop)

    for filename in mp3files:
        """
        rndfilename = mp3files[randrange(len(mp3files))]
        # Reuse existing decoder/stream object to save memory
        MP3Stream.file = open(sound_dir + rndfilename, "rb")
        # audio.play(MP3Stream)
        if verbose: print("Playing ", rndfilename)

        audio.play(mixer) # Have AudioOut play our Mixer source
        mixer.voice[0].play(synth)     # Play the first sample voice
        # mixer.voice[0].level = 0.4
        # while mixer.playing:
        #   mixer.voice[1].play(song2)    # Play another sample/voice
        """

        #################################################
        # This allows you to do other things while the audio plays!
        while True:  # audio.playing:
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
            # region Read and print LIS3DH values
            x, y, z = [
                value / adafruit_lis3dh.STANDARD_GRAVITY
                for value in lis3dh.acceleration
            ]
            if verbose and (not loop_inner % 25):
                print(
                    f"x = {x:.3f} G, y = {y:.3f} G, z = {z:.3f} G (loop:{loop_inner})"
                )

            if verbose and lis3dh.tapped:
                print("Tapped!")
            if verbose and lis3dh.shake(
                shake_threshold=12
            ):  # default of 30 is too high
                print("Shaken!")
            # endregion

            # Above code always runs
            # Code below only runs if mailbox lid is opened, in order to save battery power
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
                    key = randrange(4)
                    print("Key simulation: ", key)
                    if key == 0:
                        arpy.next_arp()  # left button changes arp played
                        print(arpy.arp_name())
                    elif key == 1:
                        steps = (
                            arpy.trans_steps + 1
                        ) % 3  # right button changes arp up iterations
                        print("steps", steps)
                        arpy.set_transpose(steps=steps)
                    elif key == 2:
                        print("key 2...")
                    elif key == 3:
                        print("key 3...")

                    # filter noisy adc

                    knobA_value = randrange(analog_max)
                    knobB_value = randrange(analog_max)
                    # knobA_value = 1
                    knobA_value = (
                        knobA_value * knobfilter + (1 - knobfilter) * knobA_value
                    )
                    knobB_value = (
                        knobB_value * knobfilter + (1 - knobfilter) * knobB_value
                    )

                    # map knobA to root note
                    arpy.root_note = int(map_range(knobA_value, 0, 65535, 24, 72))
                    # map knobB to bpm
                    arpy.set_bpm(map_range(knobB_value, 0, 65535, 40, 180))

                    arpy.update()
                    time.sleep(3)

                # -----------------
                # modify audio based on switches?
                # print (-100%8) 4
                mixer.voice[
                    0
                ].level = 0.6  # (mixer.voice[0].level - 0.1) % 0.4  # reduce

                """
                synth.press((65, 69, 72))  # midi note 65 = F4
                time.sleep(1)
                synth.release((65, 69, 72))  # release the note we pressed
                time.sleep(2)
                mixer.voice[0].level = (mixer.voice[0].level - 0.1) % 0.4  # reduce 

                print("playing sine wave")
                # if not button.value:
                audio.play(sine_wave_sample, loop=True)
                time.sleep(2)
                audio.stop()
                """

                # -----------------
                # region Modify external neopixel animation based on switches?
                # How to make responsive animations???
                # https://docs.circuitpython.org/projects/led-animation/en/latest/api.html#adafruit_led_animation.animation.Animation

                # for now nothing...
                # ...otherwise just continue next step of annimation
                # https://learn.adafruit.com/cooperative-multitasking-in-circuitpython-with-asyncio?view=all
                # animations.stopAllAnimations()
                # https://learn.adafruit.com/circuit-playground-bike-light/the-all-of-them-circuitpython
                # https://learn.adafruit.com/circuit-playground-bluefruit-neopixel-animation-and-color-remote-control/neopixel-animator-code

                # animations.speed=1
                animations.animate()

                # animations.freeze()
                # animations.resume()

                # animations.next()
                # animations.fill(color.BLACK)
                # animations.fill(color.GREEN)
                # animations.color = packet.color

                # advance_interval=2,
                # speed = 2)
                # endregion

                # -----------------
                # region Move servo back and forth
                prop_servo.angle = angle
                if angle_plus:
                    angle += 5
                else:
                    angle -= 5
                if angle == 180:
                    angle_plus = False
                elif angle == 0:
                    angle_plus = True
                # endregion

            # time.sleep(.05)
            # pass

        # print("Waiting for button press to continue!")
        # while button.value:
        #     pass


"""
    if audio.playing is False:
        print("play mp3[3]...")
        # sample = sound_dir + "lars_0{}.mp3".format(sample_number)
        # print("Now playing: '{}'".format(sample))
        # mp3stream = audiomp3.MP3Decoder(open(sound_dir + mp3files[3], "rb"))
        decoder.file = open(sound_dir + mp3files[3], "rb")
        audio.play(decoder) 
        # sample_number = (sample_number + 1) % 10
        print("DONE playing mp3[3]")
    # enable.value = audio.playing enable = speaker pin gets enabled to play
"""
