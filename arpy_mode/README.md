# Arpeggiator mode (experimental)

An 80s-style synth arpeggio, based on todbot's
[eighties_arp](https://github.com/todbot/circuitpython-synthio-tricks/tree/main/examples/eighties_arp)
example. It is kept out of the mailbox show so it can be explored on its own.

| File | Purpose |
| --- | --- |
| `arp_synth.py` | Sets up the synth and runs it; copy to the board as `code.py` |
| `arpy.py` | The `Arpy` arpeggio class; copy to the board root beside it |

Delete `code.py` and `arpy.py` from the board to go back to the normal show.

## What it does now

- Every 3 seconds it picks a random "key press" (next arp pattern, or change
  the number of octave steps) and random "knob" values that set the root note
  (MIDI 24–72) and tempo (40–180 bpm).
- The Feather's own NeoPixel changes colour with each note.

## Known issues, to sort out when exploring

- **Audio goes to the RX pin** as PWM (`audiopwmio`, a QT Py setup), not to the
  Prop-Maker's I2S amplifier and speaker terminals. To hear it on the mailbox
  speaker, switch to `audiobusio.I2SOut` as in `sound.py` and turn on
  `board.EXTERNAL_POWER`.
- **`time.sleep(3)`** in `arp_step` means `arpy.update()` runs only every 3 s,
  so it plays one note per step rather than a running arpeggio.
- **The knob "filter" does nothing:** `v * f + (1 - f) * v` is just `v`. It
  needs the previous value: `new = old * f + (1 - f) * reading`.
- The key and knob inputs are simulated with `randrange`. Real controls could
  come from the rotary encoder idea in [../IDEAS.md](../IDEAS.md).
- Not tried on the board since the 2026-10-22 move to CircuitPython 10.
