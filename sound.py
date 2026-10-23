# SPDX-FileCopyrightText: 2023 John Cornelison for Vashon Software
# SPDX-License-Identifier: MIT

"""Music & Audio: I2S output, mixer, and start-up audio tests"""

# https://github.com/todbot/circuitpython-tricks#audio

import time
import array
import math

import board
import microcontroller
from audiocore import RawSample
import audiocore  # for WAV files
import audiobusio  # for I2S audio with external I2S DAC board
import audiomixer
import audiomp3
import synthio

from config import verbose, sound_dir, mp3files

wav_file2 = "sounds/amenfull_22k_s16.wav"
# in 'circuitpython-tricks/larger-tricks/breakbeat_wavs'
mp3_file2 = (
    "sounds/OneDay_22k.mp3"
    # in 'circuitpython-tricks/larger-tricks/wav'
)
# https://freesound.org/people/f-r-a-g-i-l-e/sounds/476663/

MIXER_SAMPLE_RATE = 22050
MIXER_CHANNELS = 1

# Song volume; it ducks while the creak or whistle plays so they stand out
SONG_LEVEL = 0.6
DUCKED_LEVEL = 0.25
DUCK_DOWN = 0.1  # seconds to fade the song down when an effect starts
DUCK_UP = 0.8  # seconds to bring it back after the effects stop


def setup_audio(test_clips=True):
    """Start I2S output through a mixer; returns (audio, mixer)"""
    # i2s audio playback on PropMaker Feather RP2040
    audio = audiobusio.I2SOut(
        board.I2S_BIT_CLOCK, board.I2S_WORD_SELECT, board.I2S_DATA
    )  # aka DAC!

    # Using mixer just to enable volume control
    # voice 0: songs, voice 1: door creak, voice 2: slide whistle
    # https://learn.adafruit.com/adafruit-rp2040-prop-maker-feather/audio-mixer-volume-control
    mixer = audiomixer.Mixer(
        voice_count=3,
        channel_count=MIXER_CHANNELS,
        sample_rate=MIXER_SAMPLE_RATE,
        bits_per_sample=16,
        samples_signed=True,
    )
    audio.play(mixer)  # attach mixer to audio playback
    mixer.voice[0].level = SONG_LEVEL
    if not test_clips:
        return audio, mixer

    wave = audiocore.WaveFile(open(wav_file2, "rb"))
    mp3 = audiomp3.MP3Decoder(open(mp3_file2, "rb"))
    mixer.voice[0].play(wave)
    mixer.voice[0].level = 0.4
    mixer.voice[1].play(mp3)
    mixer.voice[1].level = 0.4
    return audio, mixer


def open_song_decoder():
    """One MP3 decoder, reused for every song to save memory"""
    return audiomp3.MP3Decoder(open(sound_dir + mp3files[0], "rb"))


def first_song_index():
    """Song to start with, kept in nvm so each door opening starts a new song

    Opening the door powers the board up, so RAM can't remember the last song.
    Erased nvm reads 0xFF, which is out of range, so that starts at song 0.
    """
    index = microcontroller.nvm[0]
    return index if index < len(mp3files) else 0


def remember_next_song(index):
    """Store the song after this one, as soon as this one starts

    Flash wears out after ~100,000 writes; one write per song is fine.
    """
    next_index = (index + 1) % len(mp3files)
    if microcontroller.nvm[0] != next_index:
        microcontroller.nvm[0] = next_index


def play_song(audio, mixer, decoder, filename):
    """Start a song; returns the object whose .playing goes False when it ends

    The mixer only accepts songs that match its sample rate & channels.
    Other songs play straight to the I2S output, without mixer volume control.
    """
    decoder.file = open(sound_dir + filename, "rb")
    if verbose:
        print(
            "Playing", filename, decoder.sample_rate, "Hz,",
            decoder.channel_count, "channel(s)",
        )
    if (
        decoder.sample_rate == MIXER_SAMPLE_RATE
        and decoder.channel_count == MIXER_CHANNELS
    ):
        if not audio.playing:
            audio.play(mixer)  # reattach the mixer after a direct song
        mixer.voice[0].play(decoder)
        return mixer.voice[0]
    audio.play(decoder)
    return audio


class SongDucker:
    """Fades the song (voice 0) down while effects play, and back up after"""

    def __init__(self, mixer):
        self.voice = mixer.voice[0]
        self.level = SONG_LEVEL
        self.last_time = time.monotonic()

    def update(self, effects_playing):
        """Call often; effects_playing is True while the creak or whistle sounds"""
        now = time.monotonic()
        elapsed, self.last_time = now - self.last_time, now
        span = SONG_LEVEL - DUCKED_LEVEL
        if effects_playing:
            self.level = max(self.level - span * elapsed / DUCK_DOWN, DUCKED_LEVEL)
        else:
            self.level = min(self.level + span * elapsed / DUCK_UP, SONG_LEVEL)
        if self.voice.level != self.level:
            self.voice.level = self.level


def make_sine_wave_sample(frequency=440, volume=0.1):
    """Simple tone sample, signed & at the mixer's sample rate so the mixer takes it"""
    # https://github.com/todbot/circuitpython-tricks#making-simple-tones
    length = MIXER_SAMPLE_RATE // frequency
    sine_wave = array.array("h", [0] * length)
    for i in range(length):
        sine_wave[i] = int(math.sin(math.pi * 2 * i / length) * volume * (2**15 - 1))
    return RawSample(sine_wave, sample_rate=MIXER_SAMPLE_RATE)


def play_test_sounds(audio, mixer):
    """Load and try out each kind of audio source"""
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
    # Play a WAV file (e.g., from
    # https://github.com/KristofferKarlAxelEkstrand/AKWF-FREE,
    # https://WaveEditOnline.com)
    wav_song = audiocore.WaveFile(open(sound_dir + "bowing.wav", "rb"))  # 16 & 44100
    if verbose:
        bps = wav_song.bits_per_sample  # 16
        sr = wav_song.sample_rate  # 44100
        print("WAV song bps:", bps, " sample rate:", sr)

    # ######## Play Midi
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

    # ####### Create Synth
    synth = synthio.Synthesizer(channel_count=1, sample_rate=9990)
    if verbose:
        bps = "undefined"  # synth.bits_per_sample
        sr = synth.sample_rate  # 9990
        print("Synth sample bps:", bps, " sample rate:", sr)

    # ###### Create sine wave sample
    sine_wave_sample = make_sine_wave_sample()
    if verbose:
        bps = "undefined"  # sine_wave_sample.bits_per_sample
        sr = sine_wave_sample.sample_rate  # 8000
        print("sine_wave_sample sample bps:", bps, " sample rate:", sr)

    # ######### Play some of the above...
    print("sine_wavesample rate: ", sine_wave_sample.sample_rate)  # 22050
    audio.play(mixer)  # reattach the mixer; the melody played straight to I2S
    mixer.voice[1].play(sine_wave_sample, loop=True)
    mixer.voice[1].level = 0.4
    if verbose:
        print("Mixer voice 1 playing...")
    time.sleep(1)
    mixer.voice[1].stop()
