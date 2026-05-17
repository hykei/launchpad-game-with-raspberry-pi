from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable


BOARD_SIZE = 8


class Player(str, Enum):
    RED = "red"
    WHITE = "white"

    @property
    def opponent(self) -> "Player":
        return Player.WHITE if self is Player.RED else Player.RED

    @property
    def forward(self) -> int:
        return -1 if self is Player.RED else 1


@dataclass(frozen=True)
class Piece:
    player: Player
    king: bool = False


@dataclass(frozen=True)
class Pos:
    x: int
    y: int

    @classmethod
    def from_algebraic(cls, value: str) -> "Pos":
        if len(value) != 2:
            raise ValueError(f"bad square: {value!r}")
        file_char, rank_char = value[0].lower(), value[1]
        if file_char < "a" or file_char > "h" or not rank_char.isdigit():
            raise ValueError(f"bad square: {value!r}")
        rank = int(rank_char)
        if rank < 1 or rank > 8:
            raise ValueError(f"bad square: {value!r}")
        return cls(ord(file_char) - ord("a"), BOARD_SIZE - rank)

    def to_algebraic(self) -> str:
        return f"{chr(ord('a') + self.x)}{BOARD_SIZE - self.y}"


@dataclass(frozen=True)
class Move:
    start: Pos
    end: Pos


@dataclass(frozen=True)
class MoveResult:
    captured: Piece | None
    crowned: bool
    winner: Player | None
    message: str


class InvalidMove(ValueError):
    pass


class CheckersGame:
    def __init__(self) -> None:
        self.board: list[list[Piece | None]] = self._new_board()
        self.turn = Player.RED
        self.red_captures = 0
        self.white_captures = 0
        self.winner: Player | None = None
        self.message = "Red to move"
        self.forced_from: Pos | None = None

    def reset(self) -> None:
        self.__init__()

    def piece_at(self, pos: Pos) -> Piece | None:
        self._assert_inside(pos)
        return self.board[pos.y][pos.x]

    def legal_moves(self, player: Player | None = None) -> list[Move]:
        player = player or self.turn
        moves: list[Move] = []
        jumps: list[Move] = []
        for y, row in enumerate(self.board):
            for x, piece in enumerate(row):
                if piece is None or piece.player is not player:
                    continue
                pos = Pos(x, y)
                for move in self._piece_moves(pos, piece, jump_only=False):
                    if abs(move.end.x - move.start.x) == 2:
                        jumps.append(move)
                    else:
                        moves.append(move)
        return jumps or moves

    def apply(self, move: Move) -> MoveResult:
        if self.winner is not None:
            raise InvalidMove("game is over")

        self._assert_inside(move.start)
        self._assert_inside(move.end)
        piece = self.piece_at(move.start)
        if piece is None:
            raise InvalidMove("no piece at start square")
        if piece.player is not self.turn:
            raise InvalidMove(f"it is {self.turn.value}'s turn")
        if self.forced_from is not None and move.start != self.forced_from:
            raise InvalidMove(f"must continue jump from {self.forced_from.to_algebraic()}")
        if self.piece_at(move.end) is not None:
            raise InvalidMove("end square is occupied")
        if not self._is_dark(move.end):
            raise InvalidMove("pieces must move on dark squares")

        legal = self.legal_moves(self.turn)
        if move not in legal:
            if any(abs(item.end.x - item.start.x) == 2 for item in legal):
                raise InvalidMove("a capture is available and must be taken")
            raise InvalidMove("illegal move")

        dx = move.end.x - move.start.x
        dy = move.end.y - move.start.y
        captured: Piece | None = None
        if abs(dx) == 2 and abs(dy) == 2:
            middle = Pos(move.start.x + dx // 2, move.start.y + dy // 2)
            captured = self.piece_at(middle)
            self.board[middle.y][middle.x] = None
            if piece.player is Player.RED:
                self.red_captures += 1
            else:
                self.white_captures += 1

        crowned = self._should_crown(piece, move.end)
        moved_piece = Piece(piece.player, piece.king or crowned)
        self.board[move.start.y][move.start.x] = None
        self.board[move.end.y][move.end.x] = moved_piece

        if captured and not crowned and self._piece_jumps(move.end, moved_piece):
            self.forced_from = move.end
            self.message = f"{piece.player.value.title()} must continue jump"
            return MoveResult(captured, crowned, None, self.message)

        self.forced_from = None
        self.turn = self.turn.opponent
        self.winner = self._find_winner()
        if self.winner:
            self.message = f"{self.winner.value.title()} wins"
        else:
            self.message = f"{self.turn.value.title()} to move"
        return MoveResult(captured, crowned, self.winner, self.message)

    def as_cells(self) -> list[list[Piece | None]]:
        return [[cell for cell in row] for row in self.board]

    def _piece_moves(self, pos: Pos, piece: Piece, jump_only: bool) -> Iterable[Move]:
        for dx, dy in self._directions(piece):
            step = Pos(pos.x + dx, pos.y + dy)
            jump = Pos(pos.x + dx * 2, pos.y + dy * 2)
            if not jump_only and self._inside(step) and self.piece_at(step) is None:
                yield Move(pos, step)
            if not self._inside(jump):
                continue
            middle = self.piece_at(step) if self._inside(step) else None
            if middle and middle.player is piece.player.opponent and self.piece_at(jump) is None:
                yield Move(pos, jump)

    def _piece_jumps(self, pos: Pos, piece: Piece) -> list[Move]:
        return [
            move
            for move in self._piece_moves(pos, piece, jump_only=True)
            if abs(move.end.x - move.start.x) == 2
        ]

    def _find_winner(self) -> Player | None:
        players_with_pieces = {
            piece.player
            for row in self.board
            for piece in row
            if piece is not None
        }
        if Player.RED not in players_with_pieces:
            return Player.WHITE
        if Player.WHITE not in players_with_pieces:
            return Player.RED
        if not self.legal_moves(self.turn):
            return self.turn.opponent
        return None

    @staticmethod
    def _new_board() -> list[list[Piece | None]]:
        board: list[list[Piece | None]] = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        for y in range(3):
            for x in range(BOARD_SIZE):
                if (x + y) % 2 == 1:
                    board[y][x] = Piece(Player.WHITE)
        for y in range(5, 8):
            for x in range(BOARD_SIZE):
                if (x + y) % 2 == 1:
                    board[y][x] = Piece(Player.RED)
        return board

    @staticmethod
    def _is_dark(pos: Pos) -> bool:
        return (pos.x + pos.y) % 2 == 1

    @staticmethod
    def _inside(pos: Pos) -> bool:
        return 0 <= pos.x < BOARD_SIZE and 0 <= pos.y < BOARD_SIZE

    @classmethod
    def _assert_inside(cls, pos: Pos) -> None:
        if not cls._inside(pos):
            raise InvalidMove(f"square outside board: {pos}")

    @staticmethod
    def _directions(piece: Piece) -> tuple[tuple[int, int], ...]:
        if piece.king:
            return ((-1, -1), (1, -1), (-1, 1), (1, 1))
        return ((-1, piece.player.forward), (1, piece.player.forward))

    @staticmethod
    def _should_crown(piece: Piece, end: Pos) -> bool:
        return not piece.king and (
            piece.player is Player.RED and end.y == 0
            or piece.player is Player.WHITE and end.y == BOARD_SIZE - 1
        )
