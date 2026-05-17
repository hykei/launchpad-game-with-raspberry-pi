# Architecture

The code is organized around three layers:

## Game Logic

Pure game modules contain rules and state:

- `hykei_games.checkers`
- `hykei_games.chess_game`
- `hykei_games.othello_game`

These modules do not depend on Raspberry Pi hardware, which keeps them easy to
test locally.

## Rendering

`hykei_games.display` converts game state into an 8x8 RGB grid and LCD status
lines.

The same rendered grid is sent to both:

- LaunchPad MK2
- Sense HAT LED matrix

## Hardware Adapters

`hykei_games.hardware` contains adapters for:

- LaunchPad MIDI input/output
- Sense HAT LEDs
- I2C LCD
- Console simulator output

The LaunchPad adapter sends RGB SysEx frames to the MK2 and reads note events
for grid/menu input.

## Controller

`hykei_games.app` owns:

- Active game selection
- Menu handling
- Board rotation
- Game-specific input dispatch
- Full display refresh after reset/rotate/game switch

The game cycle is:

```text
Checkers -> Chess -> Othello -> Checkers
```
