# Questions for John

## DiscoBox

- **Q1** (2026-10-22): Where is the VL53L1X distance sensor mounted, and which
  way does it point: down into the box toward the floor, or across the mail
  slot? Mail in/out detection (IDEAS.md) needs it pointing into the box.
  - ✅ 2026-10-22: at the back, facing the front, with the lights and speaker.
    IDEAS.md updated.
- **Q2** (2026-10-22): Which effect should be built first: the slide whistle,
  the mail in/out voice lines, or a door-angle effect (creak, volume, lights)?
  - ✅ 2026-10-22: the cartoon door creak. Built in creak.py.
- **Q3** (2026-10-22): How does the creak sound on a real door swing? Too
  loud, too quiet, too low or high, or does it creak when the door isn't
  moving? (Tuning numbers are at the top of creak.py.)
  - 2026-10-22 (bench test, transducer, no song): quiet; sounds like static
    under the song. Version A (creak.py, 55-140 Hz) sounds more like a creak;
    version B (250-600 Hz, louder, wobbly) sounds like a voice. Silent when
    the board is still. Undecided: tune further or pick another sound (Q4).
- **Q4** (2026-10-22): Keep working on the creak, or replace it with a
  different door sound (e.g. a recorded creak WAV, a slide whistle, a "boing")?
- **Q5** (2026-10-22): How does the slide whistle (whistle.py) sound when a
  hand or mail passes through the beam? Too loud or quiet, too high or low,
  does it play when nothing moves, and does the song crackle now that three
  sounds share the mixer? (Tuning numbers are at the top of whistle.py.)
  - ✅ 2026-10-22: not like a whistle, but reasonable; a bit higher. PITCH
    raised from 1800-500 Hz to 2500-700 Hz.
- **Q6** (2026-10-22): Is the higher whistle (2500-700 Hz) better? Want it
  more whistle-like (a little wobble/vibrato, like a real slide whistle)?
