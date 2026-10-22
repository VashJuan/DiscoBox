# SPDX-FileCopyrightText: 2023 John Cornelison for Vashon Software
# SPDX-License-Identifier: MIT

"""Disco Mailbox settings shared by all modules"""

verbose = True  # print debug information to serial port
# verbose = False   # no debug information to serial port

sound_dir = "sounds/"
mp3files = [
    "ClassicalGas.mp3",
    "happy.mp3",
    "fire.mp3",
    "slow.mp3",
    "Africa.mp3",
    "oneday.mp3",
]

play_arpy = False  # use the Arpy arpeggiator instead of the audio tests
