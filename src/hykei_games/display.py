from __future__ import annotations

import chess

from .checkers import BOARD_SIZE, CheckersGame, Piece, Player, Pos
from .chess_game import ChessGame
from .othello_game import Disc, OthelloGame

Color = tuple[int, int, int]
Grid = list[list[Color]]

BLACK: Color = (0, 0, 0)
DARK_SQUARE: Color = (8, 8, 8)
SELECTED: Color = (0, 70, 180)
LEGAL_MOVE: Color = (0, 130, 45)
RED_MAN: Color = (170, 0, 0)
RED_KING: Color = (255, 80, 60)
WHITE_MAN: Color = (180, 180, 160)
WHITE_KING: Color = (255, 255, 230)

CHESS_LIGHT: Color = (12, 12, 12)
CHESS_DARK: Color = (2, 2, 2)
WHITE_CHESS_COLORS: dict[int, Color] = {
    chess.PAWN: (235, 235, 235),
    chess.KNIGHT: (0, 185, 255),
    chess.BISHOP: (0, 230, 120),
    chess.ROOK: (80, 120, 255),
    chess.QUEEN: (205, 95, 255),
    chess.KING: (255, 235, 70),
}
BLACK_CHESS_COLORS: dict[int, Color] = {
    chess.PAWN: (255, 55, 0),
    chess.KNIGHT: (255, 0, 0),
    chess.BISHOP: (255, 135, 0),
    chess.ROOK: (0, 0, 255),
    chess.QUEEN: (255, 0, 180),
    chess.KING: (255, 230, 0),
}

OTHELLO_BLACK: Color = (220, 0, 0)
OTHELLO_WHITE: Color = (240, 240, 225)
OTHELLO_LEGAL: Color = (0, 110, 45)
OTHELLO_BOARD: Color = (0, 32, 12)


def render_checkers(game: CheckersGame, selected: Pos | None = None, rotation: int = 0) -> Grid:
    legal_ends = {
        move.end
        for move in game.legal_moves()
        if selected is not None and move.start == selected
    }
    grid: Grid = []
    for y in range(BOARD_SIZE):
        row: list[Color] = []
        for x in range(BOARD_SIZE):
            pos = Pos(x, y)
            piece = game.piece_at(pos)
            color = _piece_color(piece) if piece else (DARK_SQUARE if (x + y) % 2 == 1 else BLACK)
            if pos in legal_ends:
                color = LEGAL_MOVE
            if selected == pos:
                color = SELECTED
            row.append(color)
        grid.append(row)
    return rotate_grid(grid, rotation)


def render_chess(game: ChessGame, selected: Pos | None = None, rotation: int = 0) -> Grid:
    legal_ends = set(game.legal_moves_from(selected)) if selected is not None else set()
    grid: Grid = []
    for y in range(BOARD_SIZE):
        row: list[Color] = []
        for x in range(BOARD_SIZE):
            pos = Pos(x, y)
            piece = game.piece_at(pos)
            color = _chess_piece_color(piece) if piece else (CHESS_LIGHT if (x + y) % 2 == 0 else CHESS_DARK)
            if pos in legal_ends:
                color = LEGAL_MOVE
            if selected == pos:
                color = SELECTED
            row.append(color)
        grid.append(row)
    return rotate_grid(grid, rotation)


def render_othello(game: OthelloGame, rotation: int = 0) -> Grid:
    legal_moves = set(game.legal_moves())
    grid: Grid = []
    for y in range(BOARD_SIZE):
        row: list[Color] = []
        for x in range(BOARD_SIZE):
            pos = Pos(x, y)
            disc = game.disc_at(pos)
            if disc is Disc.BLACK:
                color = OTHELLO_BLACK
            elif disc is Disc.WHITE:
                color = OTHELLO_WHITE
            elif pos in legal_moves:
                color = OTHELLO_LEGAL
            else:
                color = OTHELLO_BOARD
            row.append(color)
        grid.append(row)
    return rotate_grid(grid, rotation)


def rotate_pos(pos: Pos, rotation: int) -> Pos:
    rotation %= 4
    if rotation == 0:
        return pos
    if rotation == 1:
        return Pos(BOARD_SIZE - 1 - pos.y, pos.x)
    if rotation == 2:
        return Pos(BOARD_SIZE - 1 - pos.x, BOARD_SIZE - 1 - pos.y)
    return Pos(pos.y, BOARD_SIZE - 1 - pos.x)


def unrotate_pos(pos: Pos, rotation: int) -> Pos:
    return rotate_pos(pos, -rotation)


def rotate_grid(grid: Grid, rotation: int) -> Grid:
    rotation %= 4
    result = [row[:] for row in grid]
    for _ in range(rotation):
        result = [[result[BOARD_SIZE - 1 - y][x] for y in range(BOARD_SIZE)] for x in range(BOARD_SIZE)]
    return result


def status_lines(game: CheckersGame) -> tuple[str, str]:
    line1 = game.message
    line2 = f"R:{game.red_captures} W:{game.white_captures}"
    return line1[:16], line2[:16]


def chess_status_lines(game: ChessGame) -> tuple[str, str]:
    white_count = sum(1 for piece in game.board.piece_map().values() if piece.color == chess.WHITE)
    black_count = sum(1 for piece in game.board.piece_map().values() if piece.color == chess.BLACK)
    return game.message[:16], f"W:{white_count} B:{black_count}"[:16]


def othello_status_lines(game: OthelloGame) -> tuple[str, str]:
    black, white = game.counts()
    return game.message[:16], f"B:{black} W:{white}"[:16]


def _piece_color(piece: Piece | None) -> Color:
    if piece is None:
        return BLACK
    if piece.player is Player.RED:
        return RED_KING if piece.king else RED_MAN
    return WHITE_KING if piece.king else WHITE_MAN


def _chess_piece_color(piece: chess.Piece | None) -> Color:
    if piece is None:
        return BLACK
    palette = WHITE_CHESS_COLORS if piece.color == chess.WHITE else BLACK_CHESS_COLORS
    return palette[piece.piece_type]
