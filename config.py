# SPDX-FileCopyrightText: 2023 John Cornelison for Vashon Software
# SPDX-License-Identifier: MIT

"""Disco Mailbox settings shared by all modules"""

# production: fast start-up, music first, no audio tests or debug printing
production = True
# production = False  # run the start-up audio tests & print debug information

verbose = not production  # print debug information to serial port

sound_dir = "sounds/"
# 22050 Hz mono copies, to match the mixer (originals in DiscoBox_References\sounds)
mp3files = [
    "ClassicalGas_22k.mp3",
    "happy_22k.mp3",
    "Fire_22k.mp3",
    "slow_22k.mp3",
    "Africa_22k.mp3",
    "OneDay_22k.mp3",
]

play_arpy = False  # use the Arpy arpeggiator instead of the audio tests
