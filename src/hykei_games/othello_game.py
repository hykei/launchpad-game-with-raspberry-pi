from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .checkers import BOARD_SIZE, Pos


class Disc(str, Enum):
    BLACK = "black"
    WHITE = "white"

    @property
    def opponent(self) -> "Disc":
        return Disc.WHITE if self is Disc.BLACK else Disc.BLACK


@dataclass(frozen=True)
class OthelloMoveResult:
    message: str
    moved: bool
    flipped: int = 0


class OthelloGame:
    DIRECTIONS = (
        (-1, -1),
        (0, -1),
        (1, -1),
        (-1, 0),
        (1, 0),
        (-1, 1),
        (0, 1),
        (1, 1),
    )

    def __init__(self) -> None:
        self.board: list[list[Disc | None]] = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.board[3][3] = Disc.WHITE
        self.board[3][4] = Disc.BLACK
        self.board[4][3] = Disc.BLACK
        self.board[4][4] = Disc.WHITE
        self.turn = Disc.BLACK
        self.message = "Othello Black"

    def reset(self) -> None:
        self.__init__()

    def disc_at(self, pos: Pos) -> Disc | None:
        return self.board[pos.y][pos.x]

    def legal_moves(self, player: Disc | None = None) -> list[Pos]:
        player = player or self.turn
        moves: list[Pos] = []
        for y in range(BOARD_SIZE):
            for x in range(BOARD_SIZE):
                pos = Pos(x, y)
                if self.disc_at(pos) is None and self.flips_for(pos, player):
                    moves.append(pos)
        return moves

    def flips_for(self, pos: Pos, player: Disc | None = None) -> list[Pos]:
        player = player or self.turn
        if not self._inside(pos) or self.disc_at(pos) is not None:
            return []

        flips: list[Pos] = []
        for dx, dy in self.DIRECTIONS:
            line: list[Pos] = []
            scan = Pos(pos.x + dx, pos.y + dy)
            while self._inside(scan) and self.disc_at(scan) is player.opponent:
                line.append(scan)
                scan = Pos(scan.x + dx, scan.y + dy)
            if line and self._inside(scan) and self.disc_at(scan) is player:
                flips.extend(line)
        return flips

    def apply(self, pos: Pos) -> OthelloMoveResult:
        flips = self.flips_for(pos)
        if not flips:
            self.message = "Illegal Othello"
            return OthelloMoveResult(self.message, False)

        self.board[pos.y][pos.x] = self.turn
        for flip in flips:
            self.board[flip.y][flip.x] = self.turn

        moved_player = self.turn
        self.turn = self.turn.opponent
        if not self.legal_moves(self.turn):
            if not self.legal_moves(moved_player):
                self.message = self._game_over_message()
            else:
                self.message = f"{self.turn.value.title()} pass"
                self.turn = moved_player
        else:
            self.message = f"{self.turn.value.title()} move"
        return OthelloMoveResult(self.message, True, len(flips))

    def counts(self) -> tuple[int, int]:
        black = sum(cell is Disc.BLACK for row in self.board for cell in row)
        white = sum(cell is Disc.WHITE for row in self.board for cell in row)
        return black, white

    def _game_over_message(self) -> str:
        black, white = self.counts()
        if black > white:
            return "Black wins"
        if white > black:
            return "White wins"
        return "Draw"

    @staticmethod
    def _inside(pos: Pos) -> bool:
        return 0 <= pos.x < BOARD_SIZE and 0 <= pos.y < BOARD_SIZE
