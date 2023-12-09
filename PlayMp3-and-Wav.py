# https://github.com/todbot/circuitpython-tricks#audio-out-using-i2s
import board, audiobusio, audiocore, audiomp3, audiomixer
from digitalio import DigitalInOut, Pull

num_voices = 2


# provide power to the external components
sleeping = False
external_power = DigitalInOut(board.EXTERNAL_POWER)
external_power.switch_to_output(value=not sleeping)

"""
i2s_bclk, i2s_wsel, i2s_data = (
    board.GP9,
    board.GP10,
    board.GP11,
)  # BCLK, LCLK, DIN on PCM5102

audio = audiobusio.I2SOut(bit_clock=i2s_bclk, word_select=i2s_wsel, data=i2s_data)
"""

# i2s audio playback on PropMaker Feather RP2040
audio = audiobusio.I2SOut(board.I2S_BIT_CLOCK, board.I2S_WORD_SELECT, board.I2S_DATA)
mixer = audiomixer.Mixer(
    voice_count=num_voices,
    sample_rate=22050,
    channel_count=1,
    bits_per_sample=16,
    samples_signed=True,
)
audio.play(mixer)  # attach mixer to audio playback

wav_file = "sounds/amenfull_22k_s16.wav"  # in 'circuitpython-tricks/larger-tricks/breakbeat_wavs'
mp3_file = (
    "sounds/One_Day-22Hz-16kbpsConst.mp3"  # in 'circuitpython-tricks/larger-tricks/wav'
)
# https://freesound.org/people/f-r-a-g-i-l-e/sounds/476663/

wave = audiocore.WaveFile(open(wav_file, "rb"))
mp3 = audiomp3.MP3Decoder(open(mp3_file, "rb"))
mixer.voice[0].play(wave)
mixer.voice[0].level = 0.4
mixer.voice[1].play(mp3)
mixer.voice[1].level = 0.2


i = 0
while True:
    i += 1
    if not i % 250000:
        print("playing ", i)
    # pass  # both audio files play
