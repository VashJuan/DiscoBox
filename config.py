# SPDX-FileCopyrightText: 2023 John Cornelison for Vashon Software
# SPDX-License-Identifier: MIT

"""Disco Mailbox settings shared by all modules"""

verbose = True  # print debug information to serial port
# verbose = False   # no debug information to serial port

sound_dir = "sounds/"
# 22050 Hz mono copies, to match the mixer (originals kept alongside)
mp3files = [
    "ClassicalGas_22k.mp3",
    "happy_22k.mp3",
    "Fire_22k.mp3",
    "slow_22k.mp3",
    "Africa_22k.mp3",
    "OneDay_22k.mp3",
]

play_arpy = False  # use the Arpy arpeggiator instead of the audio tests
