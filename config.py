# SPDX-FileCopyrightText: 2023 John Cornelison for Vashon Software
# SPDX-License-Identifier: MIT

"""Disco Mailbox settings shared by all modules"""

# production: fast start-up, music first, no audio tests or debug printing
production = True
# production = False  # run the start-up audio tests & print debug information

verbose = not production  # print debug information to serial port

sound_dir = "sounds/"
# 22050 Hz mono copies, to match the mixer (originals in sounds_workshop/, cut by sounds_workshop/make_clips.py)
mp3files = [
    "OneDay_22k.mp3",
    "Sexbomb_22k.mp3",
    "ClassicalGas_22k.mp3",
    "Wannabe_22k.mp3",
    "TooSexy_22k.mp3",
    "YellowSubmarine_22k.mp3",
    "WhoLetTheDogsOut_22k.mp3",
    "DontWorryBeHappy_22k.mp3",
    "YMCA_22k.mp3",
    "BeatIt_22k.mp3",
    "GangnamStyle_22k.mp3",
    "Groove_22k.mp3",
    "DrunkenSailor_22k.mp3",
    "WishingWell_22k.mp3",
    "HeyYa_22k.mp3",
    "Macarena_22k.mp3",
    "Happy_22k.mp3",
    "IWillAlwaysLoveYou_22k.mp3",
    "Blue_22k.mp3",
    "Scatterlings_22k.mp3",
    "MamboNo5_22k.mp3",
    "Fire_22k.mp3",
    "Believe_22k.mp3",
    "Tubthumping_22k.mp3",
    "NeverGonnaGiveYouUp_22k.mp3",
    "Baby_22k.mp3",
    "PokerFace_22k.mp3",
    "AxelF_22k.mp3",
]

door_creak = True  # cartoon creak over the song as the door swings (creak.py)
slide_whistle = True  # tone that follows the distance sensor as mail moves (whistle.py)
