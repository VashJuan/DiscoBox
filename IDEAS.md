# DiscoBox ideas to try

Sound and light effects to experiment with over time. None of these are built
yet. Mark each one as tried, kept or dropped, with the date and a short note.

## What the hardware gives us

- **Mixer:** 2 voices at 22050 Hz mono (`sound.py`). Songs play on `voice[0]`;
  `voice[1]` is free for effects that blend over the song. Only songs at 22050 Hz
  mono go through the mixer; other songs bypass it and can't be blended with.
  More voices are possible (`voice_count=3`) if effects need to overlap.
- **Distance sensor (VL53L1X):** about 10 readings a second (100 ms timing
  budget), short range mode (up to about 1.3 m). `distance` can be `None`. Today
  it is only printed in debug mode.
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
| Slide whistle | Hold one `synthio.Note` (sine or triangle wave) on `voice[1]`; map distance to pitch while readings change; smooth the pitch so it glides | idea |
| "That tastes good" on mail in | Note the distance when the door opens; when readings settle (steady for ~1 s), a shorter distance means the pile grew | idea |
| "Here you go" on mail out | Same, but a longer distance means mail was taken | idea |
| Whistle, then voice line | Whistle while mail moves, voice clip once it settles | idea |
| Duck the song | Lower `voice[0]` while a voice clip plays, then restore | idea |
| Light flash on mail | A burst or color change on the NeoPixels when mail goes in or out | idea |

Voice clips: record them or use text-to-speech; save as 22050 Hz mono 16-bit WAV
in `sounds/`.

In/out detection only works if the sensor points down into the box (see
Questions for John.md).

## Door angle (accelerometer)

| Idea | How | Status |
| --- | --- | --- |
| Cartoon creak | Pitch follows how fast the door swings | idea |
| Volume knob | Wider open = louder song (`voice[0].level`) | idea |
| Light control | Angle sets NeoPixel color, brightness or animation speed | idea |
| Grand entrance | Rising "ta-daaa" sweep as the door opens | idea |
| Door as instrument | Angle sets synth pitch or filter, so swinging the door plays notes | idea |

## Ways to vary it over time

- A `config.py` setting per effect, so each can be turned on and off.
- Rotate effects by power-up, like the songs (store the choice in `nvm`), so the
  carrier gets a different surprise each day.
- Random choice of voice line from a small set per event.
