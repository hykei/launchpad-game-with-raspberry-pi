from __future__ import annotations

import argparse
import time
from typing import Protocol

from .chess_game import ChessGame
from .checkers import CheckersGame, InvalidMove, Move, Pos
from .display import (
    chess_status_lines,
    othello_status_lines,
    render_checkers,
    render_chess,
    render_othello,
    status_lines,
    unrotate_pos,
)
from .othello_game import OthelloGame
from .hardware import (
    ConsoleGrid,
    ConsoleStatus,
    GridOutput,
    GridPress,
    InputEvent,
    LaunchpadMidiAdapter,
    MenuPress,
    create_i2c_lcd_status,
    SenseHatAdapter,
    StatusOutput,
)


class PlayableGame(Protocol):
    name: str
    message: str

    def reset(self) -> None:
        ...

    def clear_selection(self) -> None:
        ...

    def render(self, rotation: int) -> list[list[tuple[int, int, int]]]:
        ...

    def status_lines(self) -> tuple[str, str]:
        ...

    def handle_grid_press(self, event: GridPress, rotation: int) -> None:
        ...


class CheckersPlayable:
    name = "Checkers"

    def __init__(self) -> None:
        self.game = CheckersGame()
        self.selected: Pos | None = None

    @property
    def message(self) -> str:
        return self.game.message

    def reset(self) -> None:
        self.game.reset()
        self.selected = None

    def clear_selection(self) -> None:
        self.selected = None

    def render(self, rotation: int) -> list[list[tuple[int, int, int]]]:
        return render_checkers(self.game, self.selected, rotation)

    def status_lines(self) -> tuple[str, str]:
        return status_lines(self.game)

    def handle_grid_press(self, event: GridPress, rotation: int) -> None:
        pos = unrotate_pos(Pos(event.x, event.y), rotation)
        piece = self.game.piece_at(pos)
        if self.selected is None:
            if piece and piece.player is self.game.turn:
                self.selected = pos
                self.game.message = f"{pos.to_algebraic()} selected"
            else:
                self.game.message = f"{self.game.turn.value.title()} to move"
            return
        if pos == self.selected:
            self.selected = None
            return
        try:
            result = self.game.apply(Move(self.selected, pos))
            self.selected = pos if "continue jump" in result.message else None
        except InvalidMove as exc:
            self.game.message = str(exc).title()[:16]
            if piece and piece.player is self.game.turn:
                self.selected = pos


class ChessPlayable:
    name = "Chess"

    def __init__(self) -> None:
        self.game = ChessGame()
        self.selected: Pos | None = None

    @property
    def message(self) -> str:
        return self.game.message

    def reset(self) -> None:
        self.game.reset()
        self.selected = None

    def clear_selection(self) -> None:
        self.selected = None

    def render(self, rotation: int) -> list[list[tuple[int, int, int]]]:
        return render_chess(self.game, self.selected, rotation)

    def status_lines(self) -> tuple[str, str]:
        return chess_status_lines(self.game)

    def handle_grid_press(self, event: GridPress, rotation: int) -> None:
        pos = unrotate_pos(Pos(event.x, event.y), rotation)
        if self.selected is None:
            if self.game.has_current_player_piece(pos):
                self.selected = pos
                self.game.message = f"{pos.to_algebraic()} selected"
            else:
                self.game.message = "White move" if self.game.board.turn else "Black move"
            return
        if pos == self.selected:
            self.selected = None
            return
        if self.game.has_current_player_piece(pos):
            self.selected = pos
            self.game.message = f"{pos.to_algebraic()} selected"
            return
        result = self.game.apply(self.selected, pos)
        if result.moved:
            self.selected = None


class OthelloPlayable:
    name = "Othello"

    def __init__(self) -> None:
        self.game = OthelloGame()

    @property
    def message(self) -> str:
        return self.game.message

    def reset(self) -> None:
        self.game.reset()

    def clear_selection(self) -> None:
        pass

    def render(self, rotation: int) -> list[list[tuple[int, int, int]]]:
        return render_othello(self.game, rotation)

    def status_lines(self) -> tuple[str, str]:
        return othello_status_lines(self.game)

    def handle_grid_press(self, event: GridPress, rotation: int) -> None:
        pos = unrotate_pos(Pos(event.x, event.y), rotation)
        self.game.apply(pos)


class GameController:
    def __init__(self, outputs: list[GridOutput], status: StatusOutput) -> None:
        self.games: list[PlayableGame] = [CheckersPlayable(), ChessPlayable(), OthelloPlayable()]
        self.game_index = 0
        self.outputs = outputs
        self.status = status
        self.rotation = 0
        self._needs_hard_refresh = False

    @property
    def active(self) -> PlayableGame:
        return self.games[self.game_index]

    def handle(self, event: InputEvent) -> None:
        if isinstance(event, MenuPress):
            self._handle_menu(event.name)
        else:
            self.active.handle_grid_press(event, self.rotation)
        print(
            f"Handled {event} game={self.active.name} message={self.active.message!r}",
            flush=True,
        )
        self.render()

    def render(self) -> None:
        grid = self.active.render(self.rotation)
        if self._needs_hard_refresh:
            for output in self.outputs:
                output.reset_display()
            time.sleep(0.05)
        for output in self.outputs:
            output.show(grid)
        if self._needs_hard_refresh:
            time.sleep(0.05)
            for output in self.outputs:
                output.show(grid)
            self._needs_hard_refresh = False
        self.status.write(*self.active.status_lines())

    def _handle_menu(self, name: str) -> None:
        if name == "rotate":
            self.rotation = (self.rotation + 1) % 4
            self.active.clear_selection()
            self._needs_hard_refresh = True
        elif name == "reset":
            self.active.reset()
            self.rotation = 0
            self._needs_hard_refresh = True
        elif name == "next_game":
            self.game_index = (self.game_index + 1) % len(self.games)
            self.active.reset()
            self.rotation = 0
            self._needs_hard_refresh = True
        else:
            print(f"Unknown menu: {name}", flush=True)


def run_simulator() -> None:
    controller = GameController([ConsoleGrid()], ConsoleStatus())
    controller.render()
    while True:
        raw = input("> ").strip().lower()
        if raw in {"q", "quit", "exit"}:
            return
        if raw == "reset":
            controller.handle(MenuPress("reset"))
            continue
        if raw == "rotate":
            controller.handle(MenuPress("rotate"))
            continue
        try:
            start, end = raw.split()
            move = Move(Pos.from_algebraic(start), Pos.from_algebraic(end))
            if isinstance(controller.active, CheckersPlayable):
                controller.active.game.apply(move)
                controller.active.selected = None
            else:
                controller.active.game.apply(move.start, move.end)
                controller.active.selected = None
            controller.render()
        except (ValueError, InvalidMove) as exc:
            print(f"Invalid input: {exc}")


def run_hardware(poll_seconds: float = 0.02) -> None:
    launchpad = LaunchpadMidiAdapter()
    controller = GameController(
        outputs=[launchpad, SenseHatAdapter()],
        status=create_i2c_lcd_status(),
    )
    controller.render()
    while True:
        for event in launchpad.poll_events():
            controller.handle(event)
        time.sleep(poll_seconds)


def main() -> None:
    parser = argparse.ArgumentParser(description="hykei-84 two-player games")
    parser.add_argument("--simulator", action="store_true", help="run without hardware")
    args = parser.parse_args()
    if args.simulator:
        run_simulator()
    else:
        run_hardware()


if __name__ == "__main__":
    main()
