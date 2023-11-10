# DiscoBox™

[![SWUbanner](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/banner2-direct.svg)](https://vshymanskyy.github.io/StandWithUkraine)

This DiscoBox™ application aids postal workers morale and provides a minor touch of
enlightening joy in their day.

This is a CircuitPython script, based on Adafruit's PropMaker example & tutorial at:
(https://learn.adafruit.com/adafruit-rp2040-prop-maker-feather) with significant additions
and restructuring.

It is based on (& tested with) (https://www.adafruit.com/product/5768)

Circuit Python libraries included in the base product are listed in the right column at
(https://circuitpython.org/board/adafruit_feather_rp2040_prop_maker/) Additional libraries
are gfenerally only from the AdaFruit curated libraries at:
(https://circuitpython.org/libraries)

There are additional libraries available in the Community Bundle, but we aren't currently
using any of those: (https://github.com/adafruit/CircuitPython_Community_Bundle/)

![CircuitPython](./non-dist-imgs/circuitpython_360x161.png)
(https://github.com/adafruit/circuitpython)
![CircuitPython](./non-dist-imgs/circuitpython.png)
(https://github.com/adafruit/circuitpython)

## For Users

To use and see what this application does, simply browse to <https://Rangertrak.org>.
Additional guidence follows,

### Features

- Open Source: _free_ to use & available to enhance!
- Progressive Web App (PWA) this should be able to function (in the future, possibly with
  some degredation) even if the person using this at the command post has no or
  intermittent access to the Internet or cell system.
- Periodic reports can include an editable status field and include easily searched notes
- Source code documentation uses [https://compodoc.app/guides/jsdoc-tags.html]Compodoc
- Source code is evergreen: current with latest libraries (as of fall 2022)

### Future Roadmap

- This project is moving to using
  [milestones](https://github.com/EOCOnline/rangertrak/milestones) to show what is being
  worked on next. Dates are super approximate!
- Also see the [Issues page](https://github.com/EOCOnline/rangertrak/issues) for what
  we're working on in terms of bug fixes. Feel free to add your comments to them.
- To work with out flaws! In particular one often has to refresh some pages to get them to
  display - especially the Leaflet Maps page - or screen.
- Issues should be moving from a spreadsheet to
  [the standard GitHub Issues Page](https://github.com/EOCOnline/rangertrak/issues)
- Enhance map markers to better highlight paths, teams, statuses.
- Reload data from local files.

### Installation

At the upper right of every screen, or additinoally on the
[Settings Page](https://www.RangerTrak.org/settings), You will have the option to
"Install" the application, which just streamlines access with a shortcut. The application
takes minimal space and doesn't consume resources in the background. You can uninstall it
like any other app.

## For Developers Interested in Modifying or Contributing to the Project

- Check out <contributing.md>

### To update documentation

`npm run compodoc` to regenerate the doc. `compodoc -s` to serve/view the doc at
<http://127.0.0.1:8080/> See <https://compodoc.app/guides/usage.html> and
<https://compodoc.app/> for details

### To update 3rd party libraries

Commands from Evergreen Angular:

- `npx ng update @angular/core @angular/cdk @angular/cli @angular/google-maps @angular/material`
  (maybe with ' --force' to avoid peer dependency warnings)
- `npx ng update`
- `npx npm-check-updates -u`
- `npm install`

Other useful commands:

- `npm install -g typings` - Looks for updated Typescript type files.
- `npx ng update -g` - Updates global cli & sdk
- `npm install npm@latest -g` - update npm
- `npm install -g typescript` or to update: `npm -g upgrade typescript`; to get version:
  `tsc --version` - update typescript

### To Deploy

Deploying via Google Firebase got WAY too complex with Google's recent security upgrades.

Now I just FTP it to <https://RangerTrak.org>

OLD: `ng deploy` `ng add @angular/fire` From Angular Projects, 2nd ed. pg 119 See
angular.json and firebase.json

©2023 John Cornelison, under the MIT License

![MIT License](./non-dist-imgs/MIT_License.png)

### Public Feedback & Contribution

We encourage your feedback and contributions to this repository. Content suggestions and
discussions (specific to RangerTrak) can be communicated in the following ways:

- GitHub “issues.” Each issue is a conversation about specific project work initiated by a
  member of the public.
- GitHub "discussions". Each discussion is a project communication forum. Discussions are
  not specific to elements of work like a pull request. We encourage you to browse and
  join in on discussions or start a new conversation by creating a new discussion.
- Direct changes and line edits to the content may be submitted through a "pull request"
  by clicking "Edit this page" on any site page in the repository. You do not need to
  install any software to suggest a change. You can use GitHub's in-browser editor to edit
  files and submit a pull request for your changes to be merged into the document.
  Directions on how to submit a pull request can be found on GitHub.
- Send your content suggestions or proposed revisions to the RangerTrak team via email to
  RangerTeam@eoc.online.

### Testimonials

---
