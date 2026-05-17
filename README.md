# LaunchPad Game With Raspberry Pi

Two-player 8x8 games for Raspberry Pi / hykei-84 using:

- LaunchPad 8x8 grid as both input and output
- Sense HAT 8x8 LED matrix as a mirror output
- I2C LCD for score, turn, and status

Games:

- Checkers
- Chess
- Othello

## Run in simulator mode

```bash
python3 -m hykei_games --simulator
```

Simulator controls:

- Enter moves as `b6 a5`, `c3 e5`, etc.
- Use `reset` to restart.
- Use `rotate` to rotate both LaunchPad/Sense HAT views.
- Use the LaunchPad Next Game top button to switch between Checkers and Chess.
- Use `quit` to exit.

## Run on hykei-84 hardware

Install optional hardware dependencies on the device:

```bash
python3 -m pip install -e ".[hardware]"
```

Then run:

```bash
hykei-games
```

hykei-84 is configured for a Launchpad MK2. The adapter auto-selects MIDI
ports with `Launchpad` in the name and uses MK2 grid notes `11`-`18` on the
bottom row through `81`-`88` on the top row. If a different LaunchPad model is
connected later, update `LaunchpadMidiAdapter.note_to_xy()` and `xy_to_note()`
in `src/hykei_games/hardware.py`.

Top/menu buttons:

- Rotate: top button 0
- Reset: top button 1
- Next game: top button 2

Chess uses cool/bright colors for white pieces and warm/red-orange colors for
black pieces, while still varying by piece type:

- White: pawn white, knight cyan, bishop green, rook blue, queen purple, king gold
- Black: pawn red-orange, knight red, bishop amber, rook blue, queen magenta, king yellow

Selected pieces are blue and legal destinations are green.

Othello uses red for black-player discs and white for white-player discs on a
green board. Legal moves are shown as green highlights; press a legal square to
place a disc and flip bracketed opponent discs.

## Documentation

- [Hardware setup](docs/hardware.md)
- [Game controls and rules](docs/games.md)
- [Deployment to hykei-84](docs/deployment.md)
- [Architecture](docs/architecture.md)
