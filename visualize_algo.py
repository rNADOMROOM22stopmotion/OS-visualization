import csv
import os
import struct
import sys
import zlib
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent
ALGO_MAP = {
    "FCFS": {"csv": "FCFS.csv", "dir": "FCFS"},
    "PR": {"csv": "PR.csv", "dir": "PR"},
    "RR": {"csv": "RR.csv", "dir": "RR"},
    "SJF": {"csv": "SJF.csv", "dir": "SJF"},
    "SRTF": {"csv": "SRTF.csv", "dir": "SRTF"},
}

FONT = {
    " ": ["00000", "00000", "00000", "00000", "00000", "00000", "00000"],
    "-": ["00000", "00000", "00000", "11111", "00000", "00000", "00000"],
    ".": ["00000", "00000", "00000", "00000", "00000", "01100", "01100"],
    ":": ["00000", "01100", "01100", "00000", "01100", "01100", "00000"],
    "/": ["00001", "00010", "00100", "01000", "10000", "00000", "00000"],
    "(": ["00110", "01000", "10000", "10000", "10000", "01000", "00110"],
    ")": ["01100", "00010", "00001", "00001", "00001", "00010", "01100"],
    "0": ["01110", "10001", "10011", "10101", "11001", "10001", "01110"],
    "1": ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
    "2": ["01110", "10001", "00001", "00010", "00100", "01000", "11111"],
    "3": ["11110", "00001", "00001", "01110", "00001", "00001", "11110"],
    "4": ["00010", "00110", "01010", "10010", "11111", "00010", "00010"],
    "5": ["11111", "10000", "10000", "11110", "00001", "00001", "11110"],
    "6": ["01110", "10000", "10000", "11110", "10001", "10001", "01110"],
    "7": ["11111", "00001", "00010", "00100", "01000", "01000", "01000"],
    "8": ["01110", "10001", "10001", "01110", "10001", "10001", "01110"],
    "9": ["01110", "10001", "10001", "01111", "00001", "00001", "01110"],
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "B": ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    "C": ["01110", "10001", "10000", "10000", "10000", "10001", "01110"],
    "D": ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "F": ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
    "G": ["01110", "10001", "10000", "10111", "10001", "10001", "01110"],
    "H": ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    "I": ["01110", "00100", "00100", "00100", "00100", "00100", "01110"],
    "J": ["00111", "00010", "00010", "00010", "00010", "10010", "01100"],
    "K": ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    "M": ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    "N": ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    "O": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    "P": ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    "Q": ["01110", "10001", "10001", "10001", "10101", "10010", "01101"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    "T": ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    "U": ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    "V": ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
    "W": ["10001", "10001", "10001", "10101", "10101", "10101", "01010"],
    "X": ["10001", "10001", "01010", "00100", "01010", "10001", "10001"],
    "Y": ["10001", "10001", "01010", "00100", "00100", "00100", "00100"],
    "Z": ["11111", "00001", "00010", "00100", "01000", "10000", "11111"],
}


class Canvas:
    def __init__(self, width: int = 1000, height: int = 600, background: tuple[int, int, int] = (255, 255, 255)):
        self.width = width
        self.height = height
        self.pixels = bytearray(background * width * height)

    def set_pixel(self, x: int, y: int, color: tuple[int, int, int]) -> None:
        if 0 <= x < self.width and 0 <= y < self.height:
            index = (y * self.width + x) * 3
            self.pixels[index:index + 3] = bytes(color)

    def line(self, x1: int, y1: int, x2: int, y2: int, color: tuple[int, int, int], width: int = 1) -> None:
        dx = abs(x2 - x1)
        dy = -abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        error = dx + dy

        while True:
            radius = width // 2
            for ox in range(-radius, radius + 1):
                for oy in range(-radius, radius + 1):
                    self.set_pixel(x1 + ox, y1 + oy, color)

            if x1 == x2 and y1 == y2:
                break

            e2 = 2 * error
            if e2 >= dy:
                error += dy
                x1 += sx
            if e2 <= dx:
                error += dx
                y1 += sy

    def rect(self, x: int, y: int, width: int, height: int, color: tuple[int, int, int], fill: bool = True) -> None:
        if fill:
            for yy in range(y, y + height):
                for xx in range(x, x + width):
                    self.set_pixel(xx, yy, color)
            return

        self.line(x, y, x + width, y, color)
        self.line(x, y, x, y + height, color)
        self.line(x + width, y, x + width, y + height, color)
        self.line(x, y + height, x + width, y + height, color)

    def circle(self, cx: int, cy: int, radius: int, color: tuple[int, int, int]) -> None:
        for y in range(cy - radius, cy + radius + 1):
            for x in range(cx - radius, cx + radius + 1):
                if (x - cx) ** 2 + (y - cy) ** 2 <= radius ** 2:
                    self.set_pixel(x, y, color)

    def text(self, x: int, y: int, text: str, color: tuple[int, int, int] = (35, 35, 35), scale: int = 2) -> None:
        cursor = x
        for char in text.upper():
            pattern = FONT.get(char, FONT[" "])
            for row_index, row in enumerate(pattern):
                for col_index, bit in enumerate(row):
                    if bit == "1":
                        self.rect(
                            cursor + col_index * scale,
                            y + row_index * scale,
                            scale,
                            scale,
                            color,
                        )
            cursor += 6 * scale

    def save_png(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        raw = b"".join(
            b"\x00" + self.pixels[y * self.width * 3:(y + 1) * self.width * 3]
            for y in range(self.height)
        )

        def chunk(name: bytes, data: bytes) -> bytes:
            return (
                struct.pack(">I", len(data))
                + name
                + data
                + struct.pack(">I", zlib.crc32(name + data) & 0xFFFFFFFF)
            )

        png = b"\x89PNG\r\n\x1a\n"
        png += chunk("IHDR".encode(), struct.pack(">IIBBBBB", self.width, self.height, 8, 2, 0, 0, 0))
        png += chunk("IDAT".encode(), zlib.compress(raw, 9))
        png += chunk("IEND".encode(), b"")
        path.write_bytes(png)


def _read_rows(csv_file_path: Path) -> list[dict[str, int | str]]:
    with csv_file_path.open(newline="") as csv_file:
        rows = list(csv.DictReader(csv_file))

    for row in rows:
        for column in ["Arrival_Time", "Burst_Time", "Completion_Time", "Turnaround_Time", "Waiting_Time"]:
            row[column] = int(row[column])

    return rows


def _scale(value: int, minimum: int, maximum: int, start: int, end: int) -> int:
    if maximum == minimum:
        return (start + end) // 2
    return int(start + ((value - minimum) / (maximum - minimum)) * (end - start))


def _draw_axes(canvas: Canvas, left: int, top: int, right: int, bottom: int) -> None:
    axis = (50, 50, 50)
    grid = (225, 225, 225)

    for index in range(6):
        y = bottom - int((bottom - top) * index / 5)
        canvas.line(left, y, right, y, grid)

    canvas.line(left, top, left, bottom, axis, 2)
    canvas.line(left, bottom, right, bottom, axis, 2)


def _chart_tat_wt(rows: list[dict[str, int | str]], algo: str, out_path: Path) -> None:
    canvas = Canvas()
    left, right, top, bottom = 90, 940, 95, 500
    blue = (87, 156, 214)
    red = (230, 110, 95)

    canvas.text(90, 35, f"{algo} - TAT AND WT PER PROCESS", scale=3)
    _draw_axes(canvas, left, top, right, bottom)
    canvas.text(90, 525, "PID", scale=2)
    canvas.text(18, 95, "TIME", scale=2)

    max_time = max(1, max(max(int(row["Turnaround_Time"]), int(row["Waiting_Time"])) for row in rows))
    group_width = (right - left) / max(len(rows), 1)
    bar_width = max(12, int(group_width * 0.25))

    for index, row in enumerate(rows):
        center = int(left + group_width * index + group_width / 2)
        tat_height = int((int(row["Turnaround_Time"]) / max_time) * (bottom - top))
        wt_height = int((int(row["Waiting_Time"]) / max_time) * (bottom - top))
        canvas.rect(center - bar_width - 3, bottom - tat_height, bar_width, tat_height, blue)
        canvas.rect(center + 3, bottom - wt_height, bar_width, wt_height, red)
        canvas.text(center - 18, 515, str(row["PID"]), scale=2)

    canvas.rect(705, 52, 22, 14, blue)
    canvas.text(735, 50, "TURNAROUND", scale=2)
    canvas.rect(705, 76, 22, 14, red)
    canvas.text(735, 74, "WAITING", scale=2)
    canvas.save_png(out_path)


def _chart_burst_vs_tat(rows: list[dict[str, int | str]], algo: str, out_path: Path) -> None:
    canvas = Canvas()
    left, right, top, bottom = 90, 940, 95, 500
    purple = (120, 82, 180)

    canvas.text(90, 35, f"{algo} - BURST VS TURNAROUND", scale=3)
    _draw_axes(canvas, left, top, right, bottom)
    canvas.text(405, 535, "BURST TIME", scale=2)
    canvas.text(18, 95, "TAT", scale=2)

    bursts = [int(row["Burst_Time"]) for row in rows]
    tats = [int(row["Turnaround_Time"]) for row in rows]
    min_burst, max_burst = min(bursts), max(bursts)
    min_tat, max_tat = min(tats), max(tats)

    for row in rows:
        x = _scale(int(row["Burst_Time"]), min_burst, max_burst, left + 30, right - 30)
        y = _scale(int(row["Turnaround_Time"]), min_tat, max_tat, bottom - 30, top + 30)
        canvas.circle(x, y, 8, purple)
        canvas.text(x + 12, y - 24, str(row["PID"]), scale=2)

    canvas.save_png(out_path)


def _chart_lifespan(rows: list[dict[str, int | str]], algo: str, out_path: Path) -> None:
    canvas = Canvas()
    left, right, top, bottom = 120, 940, 95, 500
    green = (63, 150, 120)
    orange = (235, 150, 65)

    canvas.text(90, 35, f"{algo} - ARRIVAL TO COMPLETION", scale=3)
    _draw_axes(canvas, left, top, right, bottom)
    canvas.text(420, 535, "SYSTEM TIME", scale=2)

    min_time = min(int(row["Arrival_Time"]) for row in rows)
    max_time = max(int(row["Completion_Time"]) for row in rows)
    row_gap = (bottom - top) / max(len(rows), 1)

    for index, row in enumerate(rows):
        y = int(top + row_gap * index + row_gap / 2)
        arrival_x = _scale(int(row["Arrival_Time"]), min_time, max_time, left + 20, right - 20)
        completion_x = _scale(int(row["Completion_Time"]), min_time, max_time, left + 20, right - 20)
        canvas.text(45, y - 10, str(row["PID"]), scale=2)
        canvas.line(arrival_x, y, completion_x, y, green, 5)
        canvas.circle(arrival_x, y, 7, orange)
        canvas.circle(completion_x, y, 7, green)

    canvas.rect(675, 52, 20, 14, orange)
    canvas.text(705, 50, "ARRIVAL", scale=2)
    canvas.rect(675, 76, 20, 14, green)
    canvas.text(705, 74, "COMPLETION", scale=2)
    canvas.save_png(out_path)


def generate_visualizations(algo_input: str, csv_dir: Path | None = None, output_root: Path | None = None) -> list[Path]:
    algo = algo_input.strip().upper()

    if algo not in ALGO_MAP:
        raise ValueError(f"Unknown algorithm '{algo_input}'. Choose from: FCFS, PR, RR, SJF, SRTF.")

    csv_dir = csv_dir or ROOT_DIR / "utils"
    output_root = output_root or ROOT_DIR / "viz"
    csv_file_path = csv_dir / ALGO_MAP[algo]["csv"]
    out_dir = output_root / ALGO_MAP[algo]["dir"]

    if not csv_file_path.exists():
        raise FileNotFoundError(f"Could not find '{csv_file_path}'. Run the {algo} scheduler first.")

    rows = _read_rows(csv_file_path)
    if not rows:
        raise ValueError(f"The CSV file '{csv_file_path}' is empty. No data to visualize.")

    os.makedirs(out_dir, exist_ok=True)

    outputs = [
        out_dir / "tat_wt_chart.png",
        out_dir / "burst_vs_tat_scatter.png",
        out_dir / "process_lifespan.png",
    ]
    _chart_tat_wt(rows, algo, outputs[0])
    _chart_burst_vs_tat(rows, algo, outputs[1])
    _chart_lifespan(rows, algo, outputs[2])

    # print(f"\nGenerated visualizations in: {out_dir}")
    # for path in outputs:
        # print(f"Saved '{path}'")

    return outputs


def main() -> None:
    print("Welcome to OS Scheduling Visualizer!")
    print("Available algorithms: FCFS, PR (Priority), RR (Round Robin), SJF, SRTF")

    try:
        algo_input = input("Please select an algorithm: ")
        generate_visualizations(algo_input)
    except (EOFError, KeyboardInterrupt):
        print("\nExiting...")
        sys.exit(0)
    except Exception as error:
        print(f"Error: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
