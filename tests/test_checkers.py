import unittest

from hykei_games.checkers import CheckersGame, InvalidMove, Move, Piece, Player, Pos
from hykei_games.display import rotate_pos, status_lines, unrotate_pos
from hykei_games.hardware import LaunchpadMidiAdapter, SafeStatus, create_i2c_lcd_status


class CheckersGameTest(unittest.TestCase):
    def test_initial_board_has_twelve_pieces_each(self) -> None:
        game = CheckersGame()

        pieces = [piece for row in game.as_cells() for piece in row if piece]

        self.assertEqual(sum(piece.player is Player.RED for piece in pieces), 12)
        self.assertEqual(sum(piece.player is Player.WHITE for piece in pieces), 12)

    def test_regular_move_changes_turn(self) -> None:
        game = CheckersGame()

        result = game.apply(Move(Pos.from_algebraic("a3"), Pos.from_algebraic("b4")))

        self.assertIsNone(result.captured)
        self.assertIs(game.turn, Player.WHITE)
        self.assertEqual(game.piece_at(Pos.from_algebraic("b4")), Piece(Player.RED))
        self.assertIsNone(game.piece_at(Pos.from_algebraic("a3")))

    def test_capture_is_mandatory(self) -> None:
        game = CheckersGame()
        game.board = [[None for _ in range(8)] for _ in range(8)]
        game.board[5][0] = Piece(Player.RED)
        game.board[4][1] = Piece(Player.WHITE)
        game.board[5][6] = Piece(Player.RED)

        with self.assertRaisesRegex(InvalidMove, "capture"):
            game.apply(Move(Pos.from_algebraic("g3"), Pos.from_algebraic("f4")))

    def test_capture_removes_piece_and_scores(self) -> None:
        game = CheckersGame()
        game.board = [[None for _ in range(8)] for _ in range(8)]
        game.board[5][0] = Piece(Player.RED)
        game.board[4][1] = Piece(Player.WHITE)

        result = game.apply(Move(Pos.from_algebraic("a3"), Pos.from_algebraic("c5")))

        self.assertEqual(result.captured, Piece(Player.WHITE))
        self.assertEqual(game.red_captures, 1)
        self.assertIsNone(game.piece_at(Pos.from_algebraic("b4")))
        self.assertEqual(game.piece_at(Pos.from_algebraic("c5")), Piece(Player.RED))

    def test_piece_crowns_on_back_rank(self) -> None:
        game = CheckersGame()
        game.board = [[None for _ in range(8)] for _ in range(8)]
        game.board[1][2] = Piece(Player.RED)

        result = game.apply(Move(Pos.from_algebraic("c7"), Pos.from_algebraic("b8")))

        self.assertTrue(result.crowned)
        self.assertEqual(game.piece_at(Pos.from_algebraic("b8")), Piece(Player.RED, king=True))

    def test_multi_jump_must_continue_from_same_piece(self) -> None:
        game = CheckersGame()
        game.board = [[None for _ in range(8)] for _ in range(8)]
        game.board[5][0] = Piece(Player.RED)
        game.board[4][1] = Piece(Player.WHITE)
        game.board[2][3] = Piece(Player.WHITE)
        game.board[5][6] = Piece(Player.RED)

        result = game.apply(Move(Pos.from_algebraic("a3"), Pos.from_algebraic("c5")))

        self.assertIn("continue jump", result.message)
        with self.assertRaisesRegex(InvalidMove, "continue jump"):
            game.apply(Move(Pos.from_algebraic("g3"), Pos.from_algebraic("f4")))
        game.apply(Move(Pos.from_algebraic("c5"), Pos.from_algebraic("e7")))
        self.assertIs(game.turn, Player.WHITE)
        self.assertEqual(game.red_captures, 2)

    def test_rotation_round_trip(self) -> None:
        pos = Pos(2, 5)

        for rotation in range(4):
            self.assertEqual(unrotate_pos(rotate_pos(pos, rotation), rotation), pos)

    def test_status_lines_report_game_message_and_score(self) -> None:
        game = CheckersGame()
        game.message = "Red must continue jump"
        game.red_captures = 3

        self.assertEqual(status_lines(game), ("Red must continu", "R:3 W:0"))

    def test_launchpad_mk2_note_mapping_round_trip(self) -> None:
        self.assertEqual(LaunchpadMidiAdapter.note_to_xy(81), (0, 0))
        self.assertEqual(LaunchpadMidiAdapter.note_to_xy(88), (7, 0))
        self.assertEqual(LaunchpadMidiAdapter.note_to_xy(11), (0, 7))
        self.assertEqual(LaunchpadMidiAdapter.note_to_xy(18), (7, 7))

        for y in range(8):
            for x in range(8):
                self.assertEqual(
                    LaunchpadMidiAdapter.note_to_xy(LaunchpadMidiAdapter.xy_to_note(x, y)),
                    (x, y),
                )

    def test_launchpad_mk2_rgb_scales_to_sysex_range(self) -> None:
        self.assertEqual(LaunchpadMidiAdapter.color_to_rgb((0, 0, 0)), (0, 0, 0))
        self.assertEqual(LaunchpadMidiAdapter.color_to_rgb((255, 255, 255)), (63, 63, 63))
        self.assertEqual(LaunchpadMidiAdapter.color_to_rgb((170, 0, 0)), (42, 0, 0))

    def test_safe_status_disables_lcd_after_write_error(self) -> None:
        class BrokenStatus:
            def __init__(self) -> None:
                self.calls = 0

            def write(self, line1: str, line2: str) -> None:
                self.calls += 1
                raise OSError("lcd disconnected")

        broken = BrokenStatus()
        status = SafeStatus(broken)

        status.write("one", "two")
        status.write("three", "four")

        self.assertEqual(broken.calls, 1)

    def test_create_i2c_lcd_status_falls_back_when_lcd_init_fails(self) -> None:
        import hykei_games.hardware as hardware

        original = hardware.I2cLcdAdapter

        class BrokenLcd:
            def __init__(self, address: int, columns: int, rows: int) -> None:
                raise OSError("lcd disconnected")

        try:
            hardware.I2cLcdAdapter = BrokenLcd  # type: ignore[assignment]
            status = create_i2c_lcd_status()
            status.write("game", "status")
        finally:
            hardware.I2cLcdAdapter = original


if __name__ == "__main__":
    unittest.main()
