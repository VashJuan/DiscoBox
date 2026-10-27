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
  - ✅ 2026-10-22: try other sounds that suit the transducer, the songs and
    being outdoors. Five built in test_door_sounds.py (see Q7).
- **Q5** (2026-10-22): How does the slide whistle (whistle.py) sound when a
  hand or mail passes through the beam? Too loud or quiet, too high or low,
  does it play when nothing moves, and does the song crackle now that three
  sounds share the mixer? (Tuning numbers are at the top of whistle.py.)
  - ✅ 2026-10-22: not like a whistle, but reasonable; a bit higher. PITCH
    raised from 1800-500 Hz to 2500-700 Hz.
- **Q6** (2026-10-22): Is the higher whistle (2500-700 Hz) better? Want it
  more whistle-like (a little wobble/vibrato, like a real slide whistle)?
- **Q7** (2026-10-22): Run test_door_sounds.py (copy to the board as code.py)
  outdoors. Which of the five works best over the song: 1 squeak, 2 doorbell,
  3 boing, 4 ta-da, 5 cuckoo? Any too loud, quiet, harsh or long? The winner
  will play once each time the door opens.
  - ✅ 2026-10-23: all fine; 1-3 best. Squeak while the door moves, pitch
    following the angle (rising going up, falling coming down); doorbell or
    boing every ~40 s while still. Built in creak.py.
- **Q8** (2026-10-23): On the real mailbox (door vertical closed, ~110° open,
  ~20° below level): does the squeak rise going up and fall coming down? Still
  static-y? Song quiet enough under it (0.08)? Chimes too often, loud or long?
  (Tuning at the top of creak.py; CLOSED_GRAVITY may need measuring.)
- **Q9** (2026-10-23): The panel now pulses with the music (lights.py,
  MusicPulse). Does it visibly beat with the song, or is it too flickery, too
  subtle, too bright or too dim? (Tuning: PULSE_MIN/MAX, PULSE_FADE, BEAT_FLOOR
  at the top of lights.py.)
  - ✅ 2026-10-23: the beat looks good for now. Bass-beat version saved as
    an idea in IDEAS.md.
- **Q10** (2026-10-23): Run test_lights.py (copy to the board as code.py). It
  shows all 8 animations, 8 s each, with names on the serial console. Should
  any of the three switched-off ones (purple comet, amber comet, jade chase)
  join the show, or any of the five in the show be dropped?
  - ✅ 2026-10-23: add them all. All 8 are now in SHOW (lights.py).
- **Q11** (2026-10-26): Seasonal themes (plan in IDEAS.md): OK to keep all
  themes on `main` (a `themes/` folder, clips in `sounds/<theme>/`) rather
  than branches, with a deploy script that puts one theme on the board?
  - ✅ 2026-10-26: yes. Built: themes/, sounds/<theme>/, tools/deploy.ps1.
- **Q12** (2026-10-26): Which Halloween songs? Download the full songs into
  `sounds_workshop/` and add them to `songs.xlsx` (or say which and roughly
  where in each song to start). About 8-12 is enough for this year.
  - ✅ 2026-10-26: as proposed; John downloads tomorrow. 12 rows (blank start/source) in tools/songs.xlsx.
- **Q13** (2026-10-26): Haunted-house echo on the Halloween songs: yes, no,
  or try both? Any recorded sounds wanted (evil laugh, witch cackle)?
  - ✅ 2026-10-26: try both (make_clips.py --dry for without); laughs & cries: CC0 ones added.
- **Q14** (2026-10-26): Later, buy a real-time clock (DS3231, ~$14) so the
  box switches themes by date on its own?
  - ✅ 2026-10-26: yes, in the future. Saved in IDEAS.md.
- **Q15** (2026-10-26): Halloween on the board. After cutting the clips
  (`python tools/make_clips.py --theme halloween`, and `--dry` to compare):
  echo or dry? Then `pwsh tools/deploy.ps1 -Theme halloween` and copy
  `test_door_sounds.py` as `code.py` (sounds 9-13). Ghost, howl, bats, organ,
  laughs, cry & scream: too loud, quiet, long or harsh? Is the slower creak
  still static-y? Lightning flash with each chime: too bright or too much?
