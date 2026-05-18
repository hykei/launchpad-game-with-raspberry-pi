from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Union

from .display import Color, Grid


class GridOutput(Protocol):
    def show(self, grid: Grid) -> None:
        ...

    def reset_display(self) -> None:
        ...


class StatusOutput(Protocol):
    def write(self, line1: str, line2: str) -> None:
        ...


@dataclass(frozen=True)
class GridPress:
    x: int
    y: int


@dataclass(frozen=True)
class MenuPress:
    name: str


InputEvent = Union[GridPress, MenuPress]


class LaunchpadMidiAdapter:
    """LaunchPad MIDI adapter using mido.

    hykei-84 currently uses a Launchpad MK2. Its grid notes are arranged as
    11-18 on the bottom row through 81-88 on the top row.
    """

    MENU = {104: "rotate", 105: "reset", 106: "next_game"}
    LAYOUT_SESSION = (0x00, 0x20, 0x29, 0x02, 0x18, 0x22, 0x00)
    RGB_LIGHTING = (0x00, 0x20, 0x29, 0x02, 0x18, 0x0B)

    def __init__(self, input_name: str | None = None, output_name: str | None = None) -> None:
        try:
            import mido
        except ImportError as exc:
            raise RuntimeError("Install the hardware extra to use LaunchPad MIDI") from exc
        self._mido = mido
        input_name = input_name or self._find_port(mido.get_input_names())
        output_name = output_name or self._find_port(mido.get_output_names())
        print(f"LaunchPad input: {input_name}", flush=True)
        print(f"LaunchPad output: {output_name}", flush=True)
        self._input = mido.open_input(input_name)
        self._output = mido.open_output(output_name)
        self._output.send(mido.Message("sysex", data=self.LAYOUT_SESSION))

    def poll_events(self) -> list[InputEvent]:
        events: list[InputEvent] = []
        for message in self._input.iter_pending():
            if message.type not in {"note_on", "control_change"}:
                continue
            value = getattr(message, "velocity", getattr(message, "value", 0))
            if value == 0:
                continue
            note = getattr(message, "note", getattr(message, "control", -1))
            if note in self.MENU:
                events.append(MenuPress(self.MENU[note]))
                continue
            xy = self.note_to_xy(note)
            if xy is not None:
                events.append(GridPress(*xy))
        return events

    def poll(self) -> InputEvent | None:
        events = self.poll_events()
        return events[0] if events else None

    def show(self, grid: Grid) -> None:
        data: list[int] = list(self.RGB_LIGHTING)
        for y, row in enumerate(grid):
            for x, color in enumerate(row):
                note = self.xy_to_note(x, y)
                data.extend((note, *self.color_to_rgb(color)))
        self._output.send(self._mido.Message("sysex", data=data))

    def reset_display(self) -> None:
        self._output.send(self._mido.Message("sysex", data=self.LAYOUT_SESSION))
        data: list[int] = list(self.RGB_LIGHTING)
        for y in range(8):
            for x in range(8):
                data.extend((self.xy_to_note(x, y), 0, 0, 0))
        self._output.send(self._mido.Message("sysex", data=data))

    @staticmethod
    def note_to_xy(note: int) -> tuple[int, int] | None:
        x = note % 10 - 1
        y = 8 - note // 10
        if 0 <= x < 8 and 0 <= y < 8 and 1 <= note % 10 <= 8:
            return x, y
        return None

    @staticmethod
    def xy_to_note(x: int, y: int) -> int:
        return (8 - y) * 10 + x + 1

    @staticmethod
    def _find_port(names: list[str]) -> str:
        for name in names:
            if "launchpad" in name.lower():
                return name
        if names:
            return names[0]
        raise RuntimeError("No MIDI ports found for LaunchPad")

    @staticmethod
    def color_to_rgb(color: Color) -> tuple[int, int, int]:
        return tuple(min(63, max(0, round(value * 63 / 255))) for value in color)

    @staticmethod
    def color_to_velocity(color: Color) -> int:
        r, g, b = color
        if max(color) == 0:
            return 0
        if r > 200 and g > 120:
            return 63
        if r >= g and r >= b:
            return 15
        if g >= r and g >= b:
            return 60
        return 45


class SenseHatAdapter:
    def __init__(self) -> None:
        try:
            from sense_hat import SenseHat
        except ImportError as exc:
            raise RuntimeError("Install sense-hat to use the Sense HAT LED matrix") from exc
        self._sense = SenseHat()
        self._sense.low_light = True

    def show(self, grid: Grid) -> None:
        self._sense.set_pixels([color for row in grid for color in row])

    def reset_display(self) -> None:
        self._sense.clear()


class I2cLcdAdapter:
    def __init__(self, address: int = 0x27, columns: int = 16, rows: int = 2) -> None:
        try:
            from RPLCD.i2c import CharLCD
        except ImportError as exc:
            raise RuntimeError("Install RPLCD to use the I2C LCD") from exc
        self._lcd = CharLCD("PCF8574", address, cols=columns, rows=rows)

    def write(self, line1: str, line2: str) -> None:
        self._lcd.clear()
        self._lcd.write_string(line1.ljust(16)[:16])
        self._lcd.crlf()
        self._lcd.write_string(line2.ljust(16)[:16])


class SafeStatus:
    def __init__(self, wrapped: StatusOutput | None = None) -> None:
        self._wrapped = wrapped

    def write(self, line1: str, line2: str) -> None:
        if self._wrapped is None:
            print(f"LCD unavailable | {line1:<16} | {line2:<16}", flush=True)
            return
        try:
            self._wrapped.write(line1, line2)
        except OSError as exc:
            print(f"LCD disabled after write failure: {exc}", flush=True)
            self._wrapped = None


def create_i2c_lcd_status(address: int = 0x27, columns: int = 16, rows: int = 2) -> StatusOutput:
    try:
        return SafeStatus(I2cLcdAdapter(address, columns, rows))
    except (OSError, RuntimeError) as exc:
        print(f"LCD unavailable, continuing without I2C LCD: {exc}", flush=True)
        return SafeStatus()


class ConsoleStatus:
    def write(self, line1: str, line2: str) -> None:
        print(f"LCD | {line1:<16} | {line2:<16}")


class ConsoleGrid:
    def show(self, grid: Grid) -> None:
        symbols = []
        for row in grid:
            line = ""
            for color in row:
                if color == (0, 0, 0):
                    line += "."
                elif color[0] > 200 and color[1] > 100:
                    line += "K"
                elif color[0] > color[1]:
                    line += "r"
                elif color[0] > 120:
                    line += "w"
                else:
                    line += "#"
            symbols.append(line)
        print("\n".join(symbols))

    def reset_display(self) -> None:
        pass
