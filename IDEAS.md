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
| Idle chimes | Doorbell or boing every 30-50 s while the door is still (`creak.py`) | built 2026-10-23 |
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
