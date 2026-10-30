# SPDX-FileCopyrightText: 2026 John Cornelison for Vashon Software
# SPDX-License-Identifier: MIT

"""Halloween theme: pumpkin, purple & ghoul-green lights, a haunted house"""

# Lights: animation names from lights.py, shown in random order
SHOW = (
    "pumpkin comet columns",
    "pumpkin pulse",
    "candle flicker",
    "purple comet rows",
    "purple chase rows",
    "ghoul sparkle",
    "ghoul comet rows",
    "amber comet columns",
)
LIGHTNING = True  # flash the panel white as each chime starts

# Door squeak (creak.py): a slow, lower haunted-house creak.
# Not below ~300 Hz: lower sounded like static on the transducer
SQUEAK_PITCH = (700, 400)  # Hz, door closed .. fully open
SQUEAK_RASP = (8, 14)  # clicks per second, slow .. fast swing

# Chimes while the door is still: names from creak.CHIMES,
# or a 22050 Hz mono 16-bit WAV file in sounds/ (skipped if not on the board)
CHIMES = (
    "ghost",
    "howl",
    "bats",
    "organ",
    "laugh.wav",
    "laugh2.wav",
    "cry.wav",
    "scream.wav",
)

# Slide whistle (whistle.py) as a theremin: wobble in octaves
WHISTLE_VIBRATO = 0.04
# Instead of the whistle: a WAV in sounds/ when a hand or mail comes into the
# distance sensor's beam (whistle.BeamSounds); () = the whistle
BEAM_SOUNDS = ("scream.wav", "cry.wav")
