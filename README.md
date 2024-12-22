# DiscoBox™

[![SWUbanner](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/banner2-direct.svg)](https://vshymanskyy.github.io/StandWithUkraine)

## Introduction

This DiscoBox™ application aids postal workers morale and provides a minor touch
of enlightening joy in their day.

For the latest information, or to report issues, visit:
https://github.com/vashjuan/DiscoBox

## For Users

To see what this application does, browse to <https://YouTube.com/>. In the
future we'll put up a video of the mailbox disco in action!

### Color Options

- Colors defined by Adafruit Led Animation library: Amber, Aqua, Blue, Cyan,
  Gold, Green, Jade, Magenta, Old lace, Orange, Pink, Purple, Red, Teal, White,
  Yellow, Old lace (= warm white), Black, or off.

- RAINBOW is a list of colors to use for cycling through - includes, in order:
  red, orange, yellow, green, blue, and purple.

- RGBW_WHITE_RGB is for RGBW strips to illuminate only the RGB diodes

- RGBW_WHITE_RGBW is for RGBW strips to illuminate the RGB and White diodes

- RGBW_WHITE_W is for RGBW strips to illuminate only White diode

## Updating Circuit Python

1. Download the latest version of the \*.uf2 file from:
   [Feather RP2040 Prop-Maker Download](https://circuitpython.org/board/adafruit_feather_rp2040_prop_maker/)
   to a local location.

2. Enter Bootloader

> "To enter the bootloader, hold down the **BOOT/BOOTSEL** button (highlighted
> in red above), and while continuing to hold it (don't let go!), press and
> release the **reset button** (highlighted in blue above). **Continue to hold
> the BOOT/BOOTSEL button until the RPI-RP2 drive appears!**
>
> If the drive does not appear, release all the buttons, and then repeat the
> process above.
>
> You can also start with your board unplugged from USB, press and hold the
> BOOTSEL button (highlighted in red above), continue to hold it while plugging
> it into USB, and wait for the drive to appear before releasing the button."
>
> -- from https://learn.adafruit.com/adafruit-rp2040-prop-maker-feather?view=all

3. Update the PropMaker's library

Then drag the .UF2 file you downloaded onto the RPI-RP2 drive -- _not_ named
Circuit Python at this point!

A few seconds after the new \*.uf2 file is copied to the RPI-RP2 drive, the new
file is automatically installed and the drive will disappear & then show up as
CIRCUITPY again.

You're done!

### To update 3rd party libraries

Do we use any???!

### Warning!

"The JST connector polarity is matched to Adafruit LiPoly batteries. Using wrong
polarity batteries can destroy your Feather. Many customers try to save money by
purchasing Lipoly batteries from Amazon only to find that they plug them in and
the Feather is destroyed!"

### Testimonials

> _"Huh!"_
>
> - local mail carrier Craig on Vashon Island, WA

## Libraries & Background

This is a CircuitPython script, based on Adafruit's PropMaker example & tutorial
at: (https://learn.adafruit.com/adafruit-rp2040-prop-maker-feather) with
significant additions and restructuring.

It is based on (& tested with) (https://www.adafruit.com/product/5768)

Circuit Python libraries included in the base product are listed in the right
column at (https://circuitpython.org/board/adafruit_feather_rp2040_prop_maker/)
Additional libraries are generally only from the AdaFruit curated libraries at:
(https://circuitpython.org/libraries)

There are additional libraries available in the Community Bundle, but we aren't
currently using any of those:
(https://github.com/adafruit/CircuitPython_Community_Bundle/)

![CircuitPython](./non-dist-imgs/circuitpython_360x161.png)
(https://github.com/adafruit/circuitpython)
![CircuitPython](./non-dist-imgs/circuitpython.png)
(https://github.com/adafruit/circuitpython)

## Arduino CLI

https://arduino.github.io/arduino-cli/1.0/
C:\Users\John\AppData\Local\Arduino15\arduino-cli.yaml

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
- Send your content suggestions or info about your modifications on the GitHub
  site, or via email to disco (at) vashondesign.com

## License & Copyright

©2023 John Cornelison, under the MIT License

![MIT License](./non-dist-imgs/MIT_License.png) Details at
https://github.com/vashjuan/DiscoBox

---
