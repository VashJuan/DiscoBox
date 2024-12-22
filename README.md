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

### Installation

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

- Copy the `/lib/` and `/sounds/` directories, and the `main.py` file from the
  same directory as you are reading this ReadMe.md file
  (https://github.com/vashjuan/DiscoBox/ most likely) to the root directory of
  the PropMaker.

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

- Solar panel charge controller with 3.7 volt 1500 Amp-hour Lithium Ion battery

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

Although tested with version 9.2.1, any recent version of the library should
work.

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
suggestions and discussions (specific to RangerTrak) can be communicated in the
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
- Send your content suggestions or proposed revisions to the RangerTrak team via
  email to disco@vashondesign.com

### Testimonials

> _"Huh!"_
>
> -- local mail carrier Craig on Vashon Island, WA

## License & Copyright

©2023 John Cornelison, under the MIT License

Details at
[GitHub - VashJuan/DiscoBox: Delight your postal delivery person&#39;s day with a fun mailbox experience! Powered by CircuitPython](https://github.com/vashjuan/DiscoBox)
