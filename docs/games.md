# Games

Use the LaunchPad top menu buttons to rotate, reset, and switch games.

## Checkers

Checkers is a two-player game using red and white pieces.

Implemented behavior:

- Red moves first
- Normal pieces move diagonally forward
- Kings move diagonally in both directions
- Captures are mandatory
- Multi-jump captures must continue from the same piece
- Reaching the far row crowns a king
- LCD shows turn and capture counts

## Chess

Chess is powered by `python-chess` for legal move validation.

Implemented behavior:

- Standard chess movement rules
- Check, checkmate, stalemate, castling, en passant, and legal king safety
- Pawn promotion auto-promotes to queen
- Selecting a piece shows legal destination squares

Piece colors:

- White: pawn white, knight cyan, bishop green, rook blue, queen purple, king gold
- Black: pawn red-orange, knight red, bishop amber, rook blue, queen magenta, king yellow

## Othello

Othello uses red for black-player discs and white for white-player discs.

Implemented behavior:

- Black moves first
- Legal moves are shown as green highlights
- A move must bracket at least one opponent disc
- Bracketed discs flip in all 8 directions
- If the next player has no legal move, play passes automatically
- Game ends when neither player has a legal move
- LCD shows current status and disc counts
