import unittest

import chess

from hykei_games.app import GameController
from hykei_games.chess_game import ChessGame
from hykei_games.checkers import Pos
from hykei_games.display import BLACK_CHESS_COLORS, WHITE_CHESS_COLORS, render_chess
from hykei_games.hardware import ConsoleGrid, ConsoleStatus, GridPress, MenuPress


class ChessGameTest(unittest.TestCase):
    def test_pawn_moves_forward_and_captures_diagonally(self) -> None:
        game = ChessGame()

        self.assertIn(Pos.from_algebraic("e4"), game.legal_moves_from(Pos.from_algebraic("e2")))

        game.board.clear_board()
        game.board.set_piece_at(chess.E4, chess.Piece(chess.PAWN, chess.WHITE))
        game.board.set_piece_at(chess.D5, chess.Piece(chess.PAWN, chess.BLACK))
        game.board.turn = chess.WHITE

        self.assertIn(Pos.from_algebraic("d5"), game.legal_moves_from(Pos.from_algebraic("e4")))

    def test_knight_jumps_in_l_shape(self) -> None:
        game = ChessGame()

        moves = set(game.legal_moves_from(Pos.from_algebraic("g1")))

        self.assertEqual(moves, {Pos.from_algebraic("f3"), Pos.from_algebraic("h3")})

    def test_bishop_is_blocked_by_own_piece_at_start(self) -> None:
        game = ChessGame()

        self.assertEqual(game.legal_moves_from(Pos.from_algebraic("c1")), [])

    def test_illegal_move_that_exposes_king_is_rejected(self) -> None:
        game = ChessGame()
        game.board.clear_board()
        game.board.set_piece_at(chess.E1, chess.Piece(chess.KING, chess.WHITE))
        game.board.set_piece_at(chess.E2, chess.Piece(chess.ROOK, chess.WHITE))
        game.board.set_piece_at(chess.E8, chess.Piece(chess.ROOK, chess.BLACK))
        game.board.set_piece_at(chess.A8, chess.Piece(chess.KING, chess.BLACK))
        game.board.turn = chess.WHITE

        result = game.apply(Pos.from_algebraic("e2"), Pos.from_algebraic("a2"))

        self.assertFalse(result.moved)
        self.assertEqual(game.piece_at(Pos.from_algebraic("e2")), chess.Piece(chess.ROOK, chess.WHITE))

    def test_render_chess_uses_different_piece_type_colors(self) -> None:
        game = ChessGame()
        grid = render_chess(game)

        self.assertNotEqual(grid[7][0], grid[7][1])
        self.assertNotEqual(grid[7][1], grid[7][2])
        self.assertNotEqual(grid[7][3], grid[7][4])
        self.assertIn(grid[7][0], WHITE_CHESS_COLORS.values())
        self.assertIn(grid[0][0], BLACK_CHESS_COLORS.values())
        self.assertNotEqual(grid[7][0], grid[0][0])

    def test_black_chess_palette_is_pairwise_distinct_on_launchpad_scale(self) -> None:
        scaled = {
            piece_type: tuple(round(value * 63 / 255) for value in color)
            for piece_type, color in BLACK_CHESS_COLORS.items()
        }

        self.assertEqual(len(set(scaled.values())), len(BLACK_CHESS_COLORS))

    def test_next_game_switches_controller_to_chess(self) -> None:
        controller = GameController([ConsoleGrid()], ConsoleStatus())

        controller.handle(MenuPress("next_game"))
        controller.handle(GridPress(4, 6))

        self.assertEqual(controller.active.name, "Chess")
        self.assertEqual(controller.active.message, "e2 selected")


if __name__ == "__main__":
    unittest.main()
