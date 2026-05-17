from __future__ import annotations

from dataclasses import dataclass

import chess

from .checkers import Pos


@dataclass(frozen=True)
class ChessMoveResult:
    message: str
    moved: bool


class ChessGame:
    def __init__(self) -> None:
        self.board = chess.Board()
        self.message = "Chess: White"

    def reset(self) -> None:
        self.__init__()

    def piece_at(self, pos: Pos) -> chess.Piece | None:
        return self.board.piece_at(pos_to_square(pos))

    def legal_moves_from(self, pos: Pos) -> list[Pos]:
        square = pos_to_square(pos)
        return [square_to_pos(move.to_square) for move in self.board.legal_moves if move.from_square == square]

    def apply(self, start: Pos, end: Pos) -> ChessMoveResult:
        move = chess.Move(pos_to_square(start), pos_to_square(end))
        piece = self.piece_at(start)
        if piece and piece.piece_type == chess.PAWN and end.y in {0, 7}:
            move = chess.Move(move.from_square, move.to_square, promotion=chess.QUEEN)
        if move not in self.board.legal_moves:
            self.message = "Illegal chess"
            return ChessMoveResult(self.message, False)
        self.board.push(move)
        self.message = self._status_message()
        return ChessMoveResult(self.message, True)

    def has_current_player_piece(self, pos: Pos) -> bool:
        piece = self.piece_at(pos)
        return piece is not None and piece.color == self.board.turn

    def _status_message(self) -> str:
        if self.board.is_checkmate():
            winner = "Black" if self.board.turn == chess.WHITE else "White"
            return f"{winner} mate"
        if self.board.is_stalemate():
            return "Stalemate"
        if self.board.is_insufficient_material():
            return "Draw material"
        turn = "White" if self.board.turn == chess.WHITE else "Black"
        return f"{turn} check" if self.board.is_check() else f"{turn} move"


def pos_to_square(pos: Pos) -> chess.Square:
    return chess.square(pos.x, 7 - pos.y)


def square_to_pos(square: chess.Square) -> Pos:
    return Pos(chess.square_file(square), 7 - chess.square_rank(square))
