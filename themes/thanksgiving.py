# SPDX-FileCopyrightText: 2026 John Cornelison for Vashon Software
# SPDX-License-Identifier: MIT

"""Thanksgiving theme: fall colours, cold blue coming in, Pacific NW rain & storms"""

# Lights: animation names from lights.py, shown in random order.
# Mostly fall colours, with rain and bits of cold blue between
SHOW = (
    "leaf fall",
    "leaves in the rain",
    "harvest pulse",
    "candle flicker",  # the hearth
    "amber comet columns",
    "cranberry comet rows",
    "cold front",
    "ice sparkle",
    "drizzle",
    "downpour",
    "storm",
)
# Flash the panel as the thunder starts (only that chime), a cold blue-white
LIGHTNING = ("thunder",)
LIGHTNING_COLOR = (170, 210, 255)

# Door squeak (creak.py): a little lower than generic, an old wet hinge
SQUEAK_PITCH = (1000, 600)  # Hz, door closed .. fully open
SQUEAK_RASP = (14, 24)  # clicks per second, slow .. fast swing

# Chimes while the door is still: names from creak.CHIMES,
# or a 22050 Hz mono 16-bit WAV file in sounds/ (skipped if not on the board).
# Thunder twice, so storms come round more often
CHIMES = ("gobble", "geese", "patter", "wind", "thunder", "thunder")

# Slide whistle (whistle.py): a little wobble, like wind in the mail slot
WHISTLE_VIBRATO = 0.02
# WAVs in sounds/ to play instead of the whistle (whistle.BeamSounds); () = the whistle
BEAM_SOUNDS = ()
