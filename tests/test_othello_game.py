import unittest

from hykei_games.app import GameController
from hykei_games.checkers import Pos
from hykei_games.display import OTHELLO_BLACK, OTHELLO_LEGAL, OTHELLO_WHITE, render_othello
from hykei_games.hardware import ConsoleGrid, ConsoleStatus, GridPress, MenuPress
from hykei_games.othello_game import Disc, OthelloGame


class OthelloGameTest(unittest.TestCase):
    def test_initial_board_and_legal_moves(self) -> None:
        game = OthelloGame()

        self.assertEqual(game.counts(), (2, 2))
        self.assertEqual(
            set(game.legal_moves()),
            {
                Pos.from_algebraic("d6"),
                Pos.from_algebraic("c5"),
                Pos.from_algebraic("f4"),
                Pos.from_algebraic("e3"),
            },
        )

    def test_move_places_disc_and_flips_bracketed_line(self) -> None:
        game = OthelloGame()

        result = game.apply(Pos.from_algebraic("d6"))

        self.assertTrue(result.moved)
        self.assertEqual(result.flipped, 1)
        self.assertEqual(game.disc_at(Pos.from_algebraic("d6")), Disc.BLACK)
        self.assertEqual(game.disc_at(Pos.from_algebraic("d5")), Disc.BLACK)
        self.assertEqual(game.counts(), (4, 1))
        self.assertIs(game.turn, Disc.WHITE)

    def test_illegal_move_does_not_change_board(self) -> None:
        game = OthelloGame()

        result = game.apply(Pos.from_algebraic("a1"))

        self.assertFalse(result.moved)
        self.assertEqual(game.counts(), (2, 2))
        self.assertEqual(game.message, "Illegal Othello")

    def test_render_shows_discs_and_legal_moves(self) -> None:
        game = OthelloGame()
        grid = render_othello(game)

        self.assertEqual(grid[3][3], OTHELLO_WHITE)
        self.assertEqual(grid[3][4], OTHELLO_BLACK)
        self.assertEqual(grid[2][3], OTHELLO_LEGAL)

    def test_next_game_twice_switches_controller_to_othello(self) -> None:
        controller = GameController([ConsoleGrid()], ConsoleStatus())

        controller.handle(MenuPress("next_game"))
        controller.handle(MenuPress("next_game"))
        controller.handle(GridPress(3, 2))

        self.assertEqual(controller.active.name, "Othello")
        self.assertEqual(controller.active.message, "White move")


if __name__ == "__main__":
    unittest.main()
