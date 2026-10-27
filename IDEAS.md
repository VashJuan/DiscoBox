# DiscoBox ideas to try

Sound and light effects to experiment with over time. None of these are built
yet. Mark each one as tried, kept or dropped, with the date and a short note.

## What the hardware gives us

- **Mixer:** 3 voices at 22050 Hz mono (`sound.py`). Songs play on `voice[0]`,
  the creak on `voice[1]`, the slide whistle on `voice[2]`. Only songs at 22050 Hz
  mono go through the mixer; other songs bypass it and can't be blended with.
- **Distance sensor (VL53L1X):** about 10 readings a second (100 ms timing
  budget), short range mode (up to about 1.3 m). `distance` can be `None`. It
  drives the slide whistle.
- **Accelerometer (LIS3DH)** on the Feather, which is mounted on the door. The
  gravity direction gives the door angle. Needs a one-time calibration: one
  reading closed, one fully open.
- **Power:** the board only runs while the door is open, so effects happen
  during opening and while it is open, not on closing.
- **CPU:** the RP2040 is already decoding MP3. Check every synth effect for
  audio crackle.

## Mail in / mail out (distance sensor)

| Idea | How | Status |
| --- | --- | --- |
| Slide whistle | Hold one `synthio.Note` (sine wave) on `voice[2]`; map distance to pitch while readings change; smooth the pitch so it glides (`whistle.py`, `slide_whistle` in `config.py`) | built 2026-10-22, untested |
| "That tastes good" on mail in | Note the distance when the door opens; when readings settle (steady for ~1 s), a shorter distance means the pile grew | idea |
| "Here you go" on mail out | Same, but a longer distance means mail was taken | idea |
| Whistle, then voice line | Whistle while mail moves, voice clip once it settles | idea |
| Duck the song | Lower `voice[0]` while a voice clip plays, then restore | idea |
| Light flash on mail | A burst or color change on the NeoPixels when mail goes in or out | idea |

Voice clips: record them or use text-to-speech; save as 22050 Hz mono 16-bit WAV
in `sounds/`.

**Layout (John, 2026-10-22):** sensor, lights and speaker at the back of the
box, facing the front door. So the sensor measures across the box, not down at
the pile. Ideas for in/out with that layout, to test:

- Empty box, door open: long reading (or out of range). Mail lying in the beam,
  or a parcel, gives a shorter settled reading. Mount the sensor low and tilt
  it slightly down so the beam crosses the floor; flat letters may still be
  too thin to see.
- The hand or mail moving through the beam is visible either way, so the
  whistle can play for both in and out even if telling them apart fails.

## Door angle (accelerometer)

| Idea | How | Status |
| --- | --- | --- |
| Cartoon creak | Pitch, rasp & volume follow how fast the door swings | built 2026-10-22; too low & quiet for the transducer, sounds like static. Replaced by the squeak (below) |
| Angle squeak | High raspy squeak while the door moves; pitch follows the door angle (rises going up, falls coming down) (`creak.py`) | built 2026-10-23; tune on the real mailbox |
| Idle chimes | Doorbell, boing, laser, frog or saucer every 30-50 s while the door is still (`creak.py`) | built 2026-10-23 |
| Volume knob | Wider open = louder song (`voice[0].level`) | idea |
| Light control | Angle sets NeoPixel color, brightness or animation speed | idea |
| Squeak on closing | The board stays powered until the door shuts, so the closing swing squeaks too | comes with the squeak |
| Grand entrance | Rising "ta-daaa" sweep as the door opens | idea |
| Door as instrument | Angle sets synth pitch or filter, so swinging the door plays notes | idea |

### Door sounds to replace the creak

Outdoors there is no room to reflect sound, and the transducer is weak below
~300 Hz, so a door sound should be mid-to-high pitched, short, and clearly
different from the song (ducked to 0.25) and the slide whistle (a smooth sine).
Synthesized sounds cost no board space (1.1 MB free). `test_door_sounds.py`
plays these over a ducked song:

| Sound | How | Status |
| --- | --- | --- |
| Squeak | Raspy saw, 700 Hz rising most of an octave in 0.7 s: a high hinge "eeek" | chosen 2026-10-23 |
| Doorbell | "Ding-dong", E5 then C5, bell tone with harmonics, 1.2 s ring | chosen 2026-10-23 (idle chime) |
| Boing | 392 Hz triangle with a 14 Hz wobble that settles over 1 s | chosen 2026-10-23 (idle chime) |
| Ta-da | Square-wave C-E-G arpeggio, then a held high C | tried 2026-10-23; spare |
| Cuckoo | G5 to E flat 5, twice, triangle wave | tried 2026-10-23; spare |
| Laser | "Pew pew pew": three square-wave zaps, each falling 1800 to 450 Hz in 0.15 s | added 2026-10-23 (idle chime); John: fine |
| Frog | "Ribbit": two raspy 500 Hz square-wave croaks, 0.35 s each, rising half an octave | added 2026-10-23; first version (420 Hz saw, 0.18 s) too quiet to notice, made louder & longer; John: fine |
| Flying saucer | 500 Hz triangle with an 8 Hz warble, climbing 1.5 octaves over 1.5 s, then fading | added 2026-10-23 (idle chime); John: fine |
| Recorded creak WAV | A short real creak, 22 kHz mono, played on opening | idea; needs board space |

Result 2026-10-23: all were fine; squeak, doorbell & boing were best. John
chose the squeak while the door moves (pitch following the angle) and the
doorbell or boing every ~40 s while it is still. Ta-da and cuckoo are spares.

## Lights

The lights face the front from the back of the box, so most people see the
glow, not the pattern, unless they crouch and look in. Favour effects that read
as **shifting color and brightness**: slow color washes, brightness pulses on
events (mail, door swing), a color per song.

| Idea | How | Status |
| --- | --- | --- |
| Lights follow the music | `audiomp3.MP3Decoder` has an `rms_level` property (the loudness of the audio it is decoding). Read it each loop and map it to the panel's brightness (e.g. 0.02-0.3), smoothed so it pulses with the beat instead of flickering. Built as `lights.MusicPulse` | kept 2026-10-23; John: "the beat looks good for now" |
| Beat flash | Same `rms_level`; flash white or change animation when it jumps well above its recent average | idea |
| Bass-beat lights | Follow the kick drum and bass, not overall loudness. The board can't do it live: Python only gets `rms_level`, never the decoded samples, and filtering ~22,000 samples/s in Python is far too slow. Instead, find each clip's bass beats on the PC (low-pass the audio, detect onsets, e.g. with librosa) in the same script that cuts the clips, and save the beat times in a small file per song (a few hundred numbers). The board loads it when the song starts and flashes, or changes colour, at each time; almost no work while playing. Cost: one more step whenever clips are added or recut | idea 2026-10-23; only if the loudness pulse looks mushy |

## Controls

Saved from code that was switched off in `main.py` (removed 2026-10-22). Neither
was wired up in the box.

| Idea | How | Status |
| --- | --- | --- |
| Rotary encoder | [Adafruit ANO rotary encoder](https://www.adafruit.com/product/5740) on the STEMMA QT I2C bus: knob plus 5 buttons. Could set song volume, skip songs, pick an effect, or play the arpeggiator (`arpy_mode/`) | idea |
| External button | The Prop-Maker's `Btn` screw terminal (`board.EXTERNAL_BUTTON`): skip song, or a secret "party mode" | idea |

Rotary encoder setup (needs `adafruit_seesaw` back in `/lib/`; `i2c` is the
`board.STEMMA_I2C()` bus already in `main.py`):

```python
from adafruit_seesaw import seesaw, rotaryio, digitalio

ss = seesaw.Seesaw(i2c, addr=0x49)
if (ss.get_version() >> 16) & 0xFFFF != 5740:
    print("Wrong firmware loaded?  Expected 5740")
for i in range(1, 6):
    ss.pin_mode(i, ss.INPUT_PULLUP)
buttons = [digitalio.DigitalIO(ss, i) for i in range(1, 6)]
button_names = ["Select", "Up", "Left", "Down", "Right"]
button_states = [False] * 5
encoder = rotaryio.IncrementalEncoder(ss)
last_position = None

# in tick():
position = encoder.position
if position != last_position:
    last_position = position
    print("Position:", position)
for b in range(5):
    pressed = not buttons[b].value
    if pressed != button_states[b]:
        button_states[b] = pressed
        print(button_names[b], "pressed" if pressed else "released")
```

External button setup:

```python
from digitalio import DigitalInOut, Direction, Pull

button = DigitalInOut(board.EXTERNAL_BUTTON)
button.direction = Direction.INPUT
button.pull = Pull.UP  # reads False while pressed
```

## Ways to vary it over time

- A `config.py` setting per effect, so each can be turned on and off.
- Rotate effects by power-up, like the songs (store the choice in `nvm`), so the
  carrier gets a different surprise each day.
- Random choice of voice line from a small set per event.

## Seasonal themes (plan 2026-10-26)

A **theme** is a set of choices: songs, light colours and animations, door
sound, idle chimes, and how the songs are processed. "Generic" (today's
show) is one theme; Halloween, Thanksgiving, Christmas/solstice, St Patrick's
and so on are others. All themes live together on `main`, **not on branches**:
a fix to the squeak or the mixer then reaches every theme straight away,
with nothing to merge each year.

### Where things live

| Thing | Repo (keeps every theme, every year) | Board (one theme at a time) |
| --- | --- | --- |
| Theme settings | `themes/<name>.py`: palette, `SHOW` list, door sound, chime list, song volume | all `themes/*.py` (a few KB) |
| Song clips | `sounds/<name>/*.mp3` | `/sounds/` holds only the active theme's clips |
| Playlist | `sounds/<name>/playlist.txt`, written by `make_clips.py` (no more pasting into `config.py`) | copied with the clips |
| Song list & start times | `sounds_workshop/songs.xlsx` with a **Theme** column | not on the board |
| Full-length sources | `sounds_workshop/` (local only, **not backed up by git**) | not on the board |
| Which theme is on | `theme = "halloween"` in `config.py` | same |

- Code shared by all themes (`creak.py`, `lights.py`) gains a few new
  sounds and animations; a theme picks which ones to use. Nothing is
  duplicated per theme.
- **Space:** about 7.1 MB on the board. Code and libraries take ~0.5 MB, so
  one theme can have up to ~27 clips of 60 s at 32 kbps (235 KB each). A
  short season needs fewer: one song per opening, so ~8-12 clips cover a
  couple of weeks.
- **Git:** each theme adds 2-6 MB of clips once; re-cutting a clip adds it
  again. Fine for years at this rate. Tag each season's version, e.g.
  `git tag halloween-2026`, so next year starts from exactly what ran.

### Switching themes

`tools/deploy.ps1 -Theme halloween` (PowerShell 7, board on `I:`):

1. Sets `theme` in `I:\config.py`.
2. Mirrors `sounds\halloween\` to `I:\sounds\` (removes the old theme's
   clips first, so they fit).
3. Copies the code and `themes\`.

The song counter in `nvm` is saved with the theme's number, so a new theme
starts at its first song.

**Automatic by date (later):** the board has no clock that survives
power-off and no Wi-Fi, so it can't know the date. A battery-backed real-time
clock (Adafruit DS3231 on the STEMMA QT bus, about $14) would let it pick the
theme by date. All seasons' clips would still not fit in 7 MB; a microSD card
breakout (SPI) would hold every theme. Until then, switch by hand.

### Halloween (first, by 2026-10-31)

| Part | Halloween choice |
| --- | --- |
| Colours | Pumpkin orange, purple, ghoulish green, a little blood red; no rainbows |
| Animations | Orange comet, purple chase, green sparkle on purple, **candle flicker** (new: random warm flicker), **lightning** (new: white flash with each chime) |
| Songs | Spooky or Halloween songs, e.g. Thriller, Monster Mash, Ghostbusters, Time Warp, Purple People Eater, Somebody's Watching Me, This Is Halloween, Spooky Scary Skeletons, Addams Family, Werewolves of London, Toccata & Fugue in D minor (sources needed in `sounds_workshop/`) |
| Haunted-house sound | Cut on the PC: `make_clips.py` adds an echo/hall reverb (ffmpeg `aecho`) to the theme's clips. Costs nothing on the board |
| Door sound | Slow haunted-door creak: the squeak lowered to ~400-700 Hz with slower clicks (8-12/s). Not below ~300 Hz, which sounded like static on the transducer |
| Slide whistle | Theremin: the same whistle with a 5-6 Hz vibrato (also answers Q6) |
| Chimes | Synth (no board space): ghost "wooo" (sine gliding with vibrato), wolf howl, bat chirps, organ minor-chord stab. Recorded (~45 KB/s as WAV, less as MP3): evil laugh, witch cackle |

### Other themes (ideas)

| Theme | Colours | Sounds & chimes |
| --- | --- | --- |
| Thanksgiving | Amber, gold, brown, deep red | Turkey gobble chime, harvest/folk songs |
| Christmas | Red, green, warm white; twinkle sparkle | Sleigh bells, carols, "ho ho ho" |
| Solstice | Deep blue, ice white, a little gold | Wind chimes, slow bell tones |
| St Patrick's | Greens and gold | Jigs & reels; slide whistle as a tin whistle |
| Valentine's | Pink, red, magenta; heartbeat pulse | Love songs (the generic set has some) |
| July 4th | Red, white, blue; firework bursts | Firework whistle-and-pop chime, marches |
