# Hardware Setup

The project targets `hykei-84`, a Raspberry Pi-style device connected to:

- Novation Launchpad MK2
- Sense HAT 8x8 LED matrix
- 16x2 I2C LCD using a PCF8574 backpack

## LaunchPad

The Launchpad MK2 is used for both input and output.

Grid mapping:

- Top row: MIDI notes `81` through `88`
- Bottom row: MIDI notes `11` through `18`
- Coordinates are normalized to `x=0..7`, `y=0..7`
- `y=0` is the top LED row

Menu buttons:

- `104`: rotate board
- `105`: reset current game
- `106`: next game

The app auto-selects MIDI ports containing `Launchpad` in the name.

## Sense HAT

The Sense HAT mirrors the same 8x8 RGB board shown on the LaunchPad.

## I2C LCD

The LCD shows current game status and score/counts. Default address is `0x27`.

## Required System Packages

On `hykei-84`, the following packages were installed for hardware support:

```bash
sudo apt-get install -y libasound2-dev python3-sense-hat python3-rtimulib sense-hat
```
