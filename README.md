# DiscoBox™

[![SWUbanner](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/banner2-direct.svg)](https://vshymanskyy.github.io/StandWithUkraine)

## Introduction

This DiscoBox™ application aids postal workers' morale and may provide a minor
touch of enlightening joy to their day. It can easily be adapted to other
environments.

### For Users

To see what this application does, browse to
[https://YouTube.com/](https://YouTube.com/). In the future we'll put up a video
of the mailbox disco in action!

## What it does

The Prop-Maker Feather is mounted on the mailbox door and only has power while
the door is open. Opening the door starts the show; closing it ends it. All the
effects below run at the same time.

### Music

- A song starts about 0.1 s after power-up, before the lights and sensors are
  set up, so the carrier hears something straight away.
- Each power-up starts with the **next** song in the list, so the carrier gets
  a different song each day. The song number is kept in the board's `nvm`
  memory, which survives power-off.
- If the door stays open, the songs play one after another and loop back to the
  start.
- The playlist (`mp3files` in `config.py`, files in `/sounds/`):

  28 clips, 60 s each with a fade out, in priority order from
  `sounds_workshop/songs.xlsx` (every song with Priority 14 or better).
- How the clips are made (`sounds_workshop/make_clips.py`, on the PC):
  - 22050 Hz mono MP3 at **32 kbps**: 60 s is about 235 KB, so all 28 fit in
    about 6.6 MB of the board's 7.1 MB. At 48 kbps only 16 fitted.
  - 0.5 s fade in, 3 s fade out.
  - **Loudness-matched** so no song is much louder than the next. The source
    songs ranged from -25 LUFS (YMCA) to -7 LUFS (Axel F), a 19 dB spread; the
    clips now sit between -10 and -13 LUFS. The script mixes to mono at 22 kHz,
    measures, applies ffmpeg's two-pass `loudnorm` (target -12 LUFS, a little
    louder than streaming's -14, for outdoors; peaks under -2 dBTP), then
    measures the finished clip and cuts it again with a gain correction and a
    limiter if it is more than 1 dB off.

- Songs are 22050 Hz mono MP3s so they go through the audio mixer (song volume
  0.6), which lets effects such as the door creak play over them. A song in any
  other format still plays, but straight to the speaker, with no volume control
  and no effects over it.
- New clips: put the full-length song in `sounds_workshop/`, add a row
  (Priority, start, name, source) to `sounds_workshop/songs.xlsx`, run
  `python sounds_workshop/make_clips.py`, then paste the list it prints into
  `mp3files` in `config.py`. Only rows with Priority up to `MAX_PRIORITY` (14)
  are cut, so 60 s clips fit the board.

### Door squeak & chimes (`creak.py`)

- **Squeak while the door swings:** a raspy, high hinge "eeek" over the song.
  Its pitch follows the door's angle, so it rises as the door goes up and falls
  as it comes down. The faster the swing, the louder and raspier:

  | Door | Squeak |
  | --- | --- |
  | closed (vertical) | 1250 Hz |
  | fully open (110°, about 20° below level) | 700 Hz |
  | swinging under 20°/s (still) | silent |
  | swinging 20°/s | 18 clicks/s, quiet (volume 0.2) |
  | swinging 200°/s or faster | 30 clicks/s, loud (volume 0.9) |

  Pitch and volume glide to each new reading over 0.15 s, so they don't step.
  The song drops to 0.08 while the door squeaks (0.25 for the other effects).
- **Chimes while the door is still:** one picked at random every 30-50 s:
  - doorbell "ding-dong" (E5, C5)
  - cartoon "boing" (a wobbling 392 Hz tone that settles over 1 s)
  - laser "pew pew pew" (three square-wave zaps falling 1800 to 450 Hz)
  - frog "ribbit" (two raspy 500 Hz croaks, rising half an octave)
  - flying saucer (a warbling tone climbing 500 to 1400 Hz, then fading)
- The angle comes from the accelerometer's gravity reading compared with
  `CLOSED_GRAVITY`, gravity as the board sees it with the door closed (from the
  sensors.py note: y ≈ -0.9 closed). It must match how the board is mounted.
- The tuning numbers are at the top of `creak.py` (`SQUEAK_DUCKED_LEVEL` is in
  `sound.py`). Turn the door sounds off with `door_creak = False` in
  `config.py`.
- Status: built 2026-10-23 after trying five sounds with
  `test_door_sounds.py` (all fine; squeak, doorbell & boing best). First try on
  the bench sounded like static; the glide and deeper song duck were added.
  Next: tune on the real mailbox (`CLOSED_GRAVITY`, pitch direction, volume).
  The old low creak (55-140 Hz, following swing speed) sounded like static on
  the transducer.

### Slide whistle (`whistle.py`)

- When a hand or mail moves through the distance sensor's beam, a whistle
  plays over the song, gliding with the distance: about 2500 Hz at 3 cm, 700 Hz
  at 130 cm.
- It starts when a reading changes by 3 cm or more, and fades out 0.4 s after
  readings stop changing, or as soon as nothing is in range.
- It works for mail going in and coming out; telling the two apart is still an
  idea (see [IDEAS.md](IDEAS.md)).
- The tuning numbers are at the top of `whistle.py`. Turn the whistle off with
  `slide_whistle = False` in `config.py`.
- Status: tried on the board 2026-10-22: "not like a whistle, but
  reasonable". Raised from 1800-500 Hz to 2500-700 Hz to sound a bit higher.
  A little vibrato might make it more whistle-like (idea).

### Lights (`lights.py`)

- The external 8x8 NeoPixel panel (64 LEDs, brightness 5%) runs a sequence of
  eight animations, changing every 5 seconds in random order:
  - **Rainbow** – the whole rainbow scrolls across the columns
  - **Rainbow comet** – a rainbow streak bounces back and forth
  - **Rainbow chase (columns)** – rainbow bands march across the panel
  - **Rainbow chase (pixels)** – small rainbow groups chase along every pixel
  - **Rainbow sparkle** – random pixels sparkle over a rainbow
  - **Purple comet** – a purple streak bounces up and down the rows
  - **Amber comet** – an amber streak bounces across the columns
  - **Jade chase** – jade bands march along the rows
- **Lights follow the music:** the panel's brightness rises on each beat of the
  song and fades between beats (2% in quiet moments, up to 25% on the loudest
  beats). It reads the MP3 decoder's `rms_level` (loudness) and compares it with
  the song's recent loudest, so quiet and loud songs both pulse. Tuning numbers
  (`PULSE_...`) are at the top of `lights.py`; `music_lights = False` in
  `config.py` turns it off (the panel then stays at 5%).
- To see each animation on its own, copy `test_lights.py` to the board as
  `code.py`; to drop one from the show, remove its name from `SHOW` in
  `lights.py`.
- The panel sits at the back of the box facing the door, so from outside it
  mostly reads as a shifting glow of colour.

### Servo (`prop_servo.py`)

- A servo on the servo header sweeps from 0° to 180° and back, 5° every 0.07 s
  (about 2.5 s each way). It can drive any small prop. (At 5° every 0.2 s the
  servo did not move, though the code was stepping it; cause unknown.)

### Sensors

- **Accelerometer (LIS3DH, on the Feather):** drives the door squeak & chimes. In debug
  mode it also prints "Tapped!" and "Shaken!".
- **Distance sensor (VL53L1X):** measures up to about 1.3 m, about 10 times a
  second. Drives the slide whistle; in debug mode the reading is also printed.

### Arpeggiator mode (experimental)

- An 80s-style synth arpeggio, kept apart from the show in
  [`arpy_mode/`](arpy_mode/README.md). It runs on its own, instead of the
  mailbox show, and is for experimenting only. How to run it and its known
  issues are in that folder's README.

### Settings (`config.py`)

| Setting | What it does |
| --- | --- |
| `production` | `True`: fast start, music first, no debug printing. `False`: play the start-up audio tests first and print debug information to the serial console. |
| `mp3files` | The playlist, in order. |
| `door_creak` | `True` to play the door squeak & chimes. |
| `slide_whistle` | `True` to play the slide whistle. |

### Code layout

| File | Purpose |
| --- | --- |
| `main.py` | Starts the music, sets up the hardware, then runs the main loop |
| `config.py` | Settings |
| `sound.py` | Speaker output, mixer, playlist & start-up audio tests |
| `creak.py` | Door squeak & chimes |
| `whistle.py` | Slide whistle |
| `lights.py` | NeoPixel animations |
| `prop_servo.py` | Servo sweep |
| `sensors.py` | Distance sensor & accelerometer |
| `arpy_mode/` | Arpeggiator, experimental; not part of the show |
| `test_creak.py`, `test_distance.py`, `test_lights.py`, `test_servo.py` | Test one part on its own (see below) |
| `tools/` | PC-only: `make_clips.py` cuts board clips from `songs.csv` start times |
| `sounds_workshop/` | Full-length song sources (local only, not in git or on the board) |
| `references/` | Datasheets, guides & sample code (local only, not in git) |

### Testing one part at a time

Copy a test script to the board as `code.py`; CircuitPython runs `code.py`
instead of `main.py`. Each prints what it is doing to the serial console. Delete
`code.py` from the board to go back to the normal show.

| Script | What you should hear or see |
| --- | --- |
| `test_creak.py` | The old creak (no longer in `creak.py`; may need updating): a beep, then pretend door swings |
| `test_door_sounds.py` | Eight door sounds over a ducked song, each after 1-8 beeps: squeak, doorbell, boing, ta-da, cuckoo, laser, frog, saucer. With a serial console open it waits for a number (1-8, Enter); otherwise it loops through all eight |
| `test_distance.py` | A beep, the I2C addresses found (VL53L1X = `0x29`), then a tone that rises as your hand gets closer |
| `test_lights.py` | Every panel animation, 8 s each, name on the serial console |
| `test_servo.py` | The servo moves to 0°, 90°, 180° and 90°, 2 s each, then sweeps |

Ideas for new effects, and what has been tried, are in [IDEAS.md](IDEAS.md).

### Installation

![alt text](non-dist-imgs/DiscoBox-Assembled.jpg)
![alt text](non-dist-imgs/DiscoBox-Closeup.jpg)

- Attach your devices to the PropMaker. What I did:

  - On the other end from the USB connector is a 6 screw green connector with
    the following labels on the bottom of the circuit board:
  - - & - go to a 4-8 ohm (Ω) speaker
  - Btn (button) is left disconnected
  - 5V, G & Neo (5 volt positive, Ground & NeoPixel data line) are connected to
    a LED panel.
  - Immediately in front of the 6 screw green connector is a standard 3 pin
    connector for the servo motor
  - move a little towards the USB connector and (near pin 10) is a small blond
    'Grove(?)' connector with can be attached to the ToF sensor (VL53L1X for me)
  - Finally plug in a USB cord from your computer to the device's USB C plug.
    With power the PropMaker should light up. If connected and with CIrcuit Pi
    installed, you should see a new drive' on your computer.

- Install Circuit Python onto your PropMaker if necessary. (It should arrive
  from the manufacturer with that preinstalled. If not, follow directions below
  for updating the library, or go to https://Adafruit.com or
  https://CircuitPython.org for the latest instructions.)

- Copy the `/lib/` and `/sounds/` directories, and all the `*.py` files
  (`main.py`, `config.py`, `sensors.py`, `lights.py`, `sound.py`,
  `prop_servo.py`, `creak.py` and `whistle.py`) from the same directory as you
  are reading this ReadMe.md file (https://github.com/vashjuan/DiscoBox/ most
  likely) to the root directory of the PropMaker. Copy nothing else (test
  scripts, `arpy_mode/`, README, editor files): the board has only 7 MB, so
  keep it free of cruft.

- **Repo and board together:** open `DiscoBox.code-workspace` in VS Code to
  see this repo and the board's `CIRCUITPY` drive side by side. Edit in the
  repo, then copy changed files to the board; edits made only on the board are
  lost the next time you copy. The workspace expects the board at `I:`. To keep
  it there, plug in the board, open Disk Management, right-click `CIRCUITPY`,
  choose "Change Drive Letter and Paths…" and pick `I:`. Windows remembers it
  for that board.

- Check the settings in `config.py` (see [Settings](#settings-configpy) above).
  Leave `production = True` for the mailbox.

### Hardware

This is a Circuit Python script, derived from Adafruit's PropMaker example &
tutorial at: (https://learn.adafruit.com/adafruit-rp2040-prop-maker-feather)
with significant additions and restructuring.

It relies on (& tested with):

- https://www.adafruit.com/product/5768 - the Adafruit Prop Maker Feather

- an 8x8 Neopixel (or other) LED display

- A loudspeaker

- A Time of Flight sensor, in our case, a VL53L1X to measure distance to the
  incoming mail

- A generic servo motor, a Futaba 83003 for us

- Solar panel

- Solar panel charge controller with 3.7 volt 1500 mAh Lithium Ion battery

### Libraries

Circuit Python libraries included are from the base distribution listed in the
right column at
(https://circuitpython.org/board/adafruit_feather_rp2040_prop_maker/) We use a
few additional libraries, those are from the AdaFruit curated libraries at:
(https://circuitpython.org/libraries)

We don't use any of the additional libraries available in the Community Bundle:
(https://github.com/adafruit/CircuitPython_Community_Bundle/)

![CircuitPython](./non-dist-imgs/circuitpython_360x161.png)
(https://github.com/adafruit/circuitpython)
![CircuitPython](./non-dist-imgs/circuitpython.png)
(https://github.com/adafruit/circuitpython)

## Updating Circuit Python

The libraries in `/lib/` are from the CircuitPython **10.x** bundle, so the
PropMaker needs CircuitPython 10 (10.3.1 at last update). Update the firmware
before copying `/lib/` over. (Earlier code was tested with 9.2.1.)

`/lib/` holds only the libraries the code imports, plus what those need:
`adafruit_led_animation`, `neopixel` and `adafruit_pixelbuf`, `adafruit_motor`,
`adafruit_lis3dh`, `adafruit_vl53l1x` and `adafruit_bus_device`. Unused ones
(debouncer, ticks, ht16k33, midi, seesaw, wave, simpleio) were moved to
`references/Removed from board 2026-10-22/lib`. Add `adafruit_seesaw`
back if you add the rotary encoder (see [IDEAS.md](IDEAS.md#controls)).

To refresh the libraries, run [circup](https://github.com/adafruit/circup)
against this folder (it reads the version from `boot_out.txt`):

```powershell
pip install --upgrade circup
circup --path . update --all
```

1. Download the latest version of the \*.uf2 file from:
   [Feather RP2040 Prop-Maker Download](https://circuitpython.org/board/adafruit_feather_rp2040_prop_maker/)
   to a local location.
2. Enter Bootloader:

"To enter the bootloader, hold down the **BOOT/BOOTSEL** button (highlighted in
red above), and while continuing to hold it (don't let go!), press and release
the **reset button** (highlighted in blue above). **Continue to hold the
BOOT/BOOTSEL button until the `RPI-RP2` drive appears!**

If the drive does not appear, release all the buttons, and then repeat the
process above.

You can also start with your board unplugged from USB, press and hold the
BOOTSEL button (highlighted in red above), continue to hold it while plugging it
into USB, and wait for the drive to appear before releasing the button."

-- from https://learn.adafruit.com/adafruit-rp2040-prop-maker-feather?view=all

3. Update the PropMaker's library

Then drag the .UF2 file you downloaded onto the `RPI-RP2` drive -- _not_ named
Circuit Python at this point!

A few seconds after the new `*.uf2` file is copied to the `RPI-RP2` drive, the
new file is automatically installed and the drive will disappear & then show up
as `CIRCUITPY` again.

You're done! This should have updated the files in the `lib` folder, but not
have touched any other folders or files on the PropMaker.

### 3rd party libraries

We do not currently use any.

![MIT License](./non-dist-imgs/MIT_License.png)

### Color Options

- Colors defined by Adafruit Led Animation library: Amber, Aqua, Blue, Cyan,
  Gold, Green, Jade, Magenta, Old lace, Orange, Pink, Purple, Red, Teal, White,
  Yellow, Old lace (= warm white), Black, or off.

- RAINBOW is a list of colors to use for cycling through - includes, in order:
  red, orange, yellow, green, blue, and purple.

- RGBW_WHITE_RGB is for RGBW strips to illuminate only the RGB diodes

- RGBW_WHITE_RGBW is for RGBW strips to illuminate the RGB and White diodes

- RGBW_WHITE_W is for RGBW strips to illuminate only White diode

### A Note on batteries

"The JST connector polarity is matched to Adafruit LiPoly batteries. Using wrong
polarity batteries can destroy your Feather. Many customers try to save money by
purchasing Lipoly batteries from Amazon only to find that they plug them in and
the Feather is destroyed!""

### Public Feedback & Contribution

We encourage your feedback and contributions to this repository. Content
suggestions and discussions (specific to DiscoBox) can be communicated in the
following ways:

- GitHub “issues.” Each issue is a conversation about specific project work
  initiated by a member of the public.
- GitHub "discussions". Each discussion is a project communication forum.
  Discussions are not specific to elements of work like a pull request. We
  encourage you to browse and join in on discussions or start a new conversation
  by creating a new discussion.
- Direct changes and line edits to the content may be submitted through a "pull
  request" by clicking "Edit this page" on any site page in the repository. You
  do not need to install any software to suggest a change. You can use GitHub's
  in-browser editor to edit files and submit a pull request for your changes to
  be merged into the document. Directions on how to submit a pull request can be
  found on GitHub.
- Send your content suggestions or proposed revisions to the DiscoBox team via
  email to disco@vashondesign.com

### Testimonials

> _"Huh!"_
>
> -- local mail carrier Craig on Vashon Island, WA

## License & Copyright

©2023 John Cornelison, under the MIT License

Details at
[GitHub - VashJuan/DiscoBox: Delight your postal delivery person&#39;s day with a fun mailbox experience! Powered by CircuitPython](https://github.com/vashjuan/DiscoBox)
