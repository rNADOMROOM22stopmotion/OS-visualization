import csv
from collections import deque
from pathlib import Path
from typing import Any


CSV_COLUMNS = [
    "PID",
    "Arrival_Time",
    "Burst_Time",
    "Completion_Time",
    "Turnaround_Time",
    "Waiting_Time",
]


def _processes_from_input(data: Any) -> list[dict[str, int | str]]:
    processes = getattr(data, "processes", data)
    normalized = []

    for index, process in enumerate(processes):
        normalized.append(
            {
                "index": index,
                "name": str(getattr(process, "name")),
                "arrival_time": int(getattr(process, "arrival_time")),
                "burst_time": int(getattr(process, "burst_time")),
                "priority": int(getattr(process, "priority", 0)),
            }
        )

    return normalized


def _rows_from_completion(
    processes: list[dict[str, int | str]],
    completion_times: dict[str, int],
) -> list[dict[str, int | str]]:
    rows = []

    for process in processes:
        pid = str(process["name"])
        arrival_time = int(process["arrival_time"])
        burst_time = int(process["burst_time"])
        completion_time = completion_times[pid]
        turnaround_time = completion_time - arrival_time
        waiting_time = turnaround_time - burst_time

        rows.append(
            {
                "PID": pid,
                "Arrival_Time": arrival_time,
                "Burst_Time": burst_time,
                "Completion_Time": completion_time,
                "Turnaround_Time": turnaround_time,
                "Waiting_Time": waiting_time,
            }
        )

    return rows


def saver(rows: list[dict[str, int | str]], filename: str) -> Path:
    path = Path(__file__).resolve().parent / filename

    with path.open("w", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    return path


def _print_table(title: str, rows: list[dict[str, int | str]]) -> None:
    print(f"\n{title}")
    print("=" * len(title))

    widths = {
        column: max(len(column), *(len(str(row[column])) for row in rows))
        for column in CSV_COLUMNS
    }
    separator = "+-" + "-+-".join("-" * widths[column] for column in CSV_COLUMNS) + "-+"
    header = "| " + " | ".join(column.ljust(widths[column]) for column in CSV_COLUMNS) + " |"

    print(separator)
    print(header)
    print(separator)
    for row in rows:
        print("| " + " | ".join(str(row[column]).ljust(widths[column]) for column in CSV_COLUMNS) + " |")
    print(separator)

    average_tat = sum(int(row["Turnaround_Time"]) for row in rows) / len(rows)
    average_wt = sum(int(row["Waiting_Time"]) for row in rows) / len(rows)
    print(f"Average Turnaround Time: {average_tat:.2f}")
    print(f"Average Waiting Time: {average_wt:.2f}")


def _compress_gantt(gantt: list[tuple[str, int, int]]) -> list[tuple[str, int, int]]:
    compressed = []

    for pid, start, end in gantt:
        if start == end:
            continue
        if compressed and compressed[-1][0] == pid and compressed[-1][2] == start:
            compressed[-1] = (pid, compressed[-1][1], end)
        else:
            compressed.append((pid, start, end))

    return compressed


def _print_gantt_chart(gantt: list[tuple[str, int, int]]) -> None:
    gantt = _compress_gantt(gantt)
    if not gantt:
        print("\nGantt Chart: No process executed.")
        return

    labels = [pid.center(max(len(pid), end - start)) for pid, start, end in gantt]
    cell_widths = [len(label) for label in labels]

    print("\nGantt Chart")
    print("+" + "+".join("-" * (width + 2) for width in cell_widths) + "+")
    print("|" + "|".join(f" {label} " for label in labels) + "|")
    print("+" + "+".join("-" * (width + 2) for width in cell_widths) + "+")

    timeline = str(gantt[0][1])
    for (_, _, end), width in zip(gantt, cell_widths):
        timeline += " " * (width + 2 - len(str(end))) + str(end)
    print(timeline)


def _finish(title: str, rows: list[dict[str, int | str]], gantt: list[tuple[str, int, int]], filename: str) -> list[dict[str, int | str]]:
    _print_table(title, rows)
    _print_gantt_chart(gantt)
    path = saver(rows, filename)
    # print(f"\nSaved CSV: {path}")
    return rows


def FCFS(data: Any) -> list[dict[str, int | str]]:
    processes = sorted(_processes_from_input(data), key=lambda p: (int(p["arrival_time"]), int(p["index"])))
    completion_times = {}
    gantt = []
    current_time = 0

    for process in processes:
        arrival_time = int(process["arrival_time"])
        burst_time = int(process["burst_time"])
        pid = str(process["name"])

        if current_time < arrival_time:
            gantt.append(("IDLE", current_time, arrival_time))
            current_time = arrival_time

        start = current_time
        current_time += burst_time
        completion_times[pid] = current_time
        gantt.append((pid, start, current_time))

    rows = _rows_from_completion(processes, completion_times)
    return _finish("First Come First Served (FCFS)", rows, gantt, "FCFS.csv")


def SJF(data: Any) -> list[dict[str, int | str]]:
    processes = _processes_from_input(data)
    remaining = processes.copy()
    completion_times = {}
    gantt = []
    current_time = 0

    while remaining:
        available = [p for p in remaining if int(p["arrival_time"]) <= current_time]

        if not available:
            next_arrival = min(int(p["arrival_time"]) for p in remaining)
            gantt.append(("IDLE", current_time, next_arrival))
            current_time = next_arrival
            continue

        process = min(available, key=lambda p: (int(p["burst_time"]), int(p["arrival_time"]), int(p["index"])))
        remaining.remove(process)

        pid = str(process["name"])
        start = current_time
        current_time += int(process["burst_time"])
        completion_times[pid] = current_time
        gantt.append((pid, start, current_time))

    rows = _rows_from_completion(processes, completion_times)
    return _finish("Shortest Job First (SJF)", rows, gantt, "SJF.csv")


def PR(data: Any) -> list[dict[str, int | str]]:
    processes = _processes_from_input(data)
    remaining = processes.copy()
    completion_times = {}
    gantt = []
    current_time = 0

    while remaining:
        available = [p for p in remaining if int(p["arrival_time"]) <= current_time]

        if not available:
            next_arrival = min(int(p["arrival_time"]) for p in remaining)
            gantt.append(("IDLE", current_time, next_arrival))
            current_time = next_arrival
            continue

        process = min(available, key=lambda p: (int(p["priority"]), int(p["arrival_time"]), int(p["index"])))
        remaining.remove(process)

        pid = str(process["name"])
        start = current_time
        current_time += int(process["burst_time"])
        completion_times[pid] = current_time
        gantt.append((pid, start, current_time))

    rows = _rows_from_completion(processes, completion_times)
    return _finish("Priority Scheduling (PR)", rows, gantt, "PR.csv")


def SRTF(data: Any) -> list[dict[str, int | str]]:
    processes = _processes_from_input(data)
    remaining_times = {str(p["name"]): int(p["burst_time"]) for p in processes}
    completion_times = {}
    gantt = []
    current_time = min((int(p["arrival_time"]) for p in processes), default=0)

    while len(completion_times) < len(processes):
        available = [
            p
            for p in processes
            if int(p["arrival_time"]) <= current_time and remaining_times[str(p["name"])] > 0
        ]

        if not available:
            next_arrival = min(
                int(p["arrival_time"])
                for p in processes
                if remaining_times[str(p["name"])] > 0
            )
            gantt.append(("IDLE", current_time, next_arrival))
            current_time = next_arrival
            continue

        process = min(
            available,
            key=lambda p: (remaining_times[str(p["name"])], int(p["arrival_time"]), int(p["index"])),
        )
        pid = str(process["name"])

        gantt.append((pid, current_time, current_time + 1))
        remaining_times[pid] -= 1
        current_time += 1

        if remaining_times[pid] == 0:
            completion_times[pid] = current_time

    rows = _rows_from_completion(processes, completion_times)
    return _finish("Shortest Remaining Time First (SRTF)", rows, gantt, "SRTF.csv")


def RR(data: Any, quantum: int = 2) -> list[dict[str, int | str]]:
    if quantum <= 0:
        raise ValueError("Quantum must be greater than 0.")

    processes = sorted(_processes_from_input(data), key=lambda p: (int(p["arrival_time"]), int(p["index"])))
    remaining_times = {str(p["name"]): int(p["burst_time"]) for p in processes}
    completion_times = {}
    gantt = []
    ready_queue = deque()
    current_time = 0
    next_process_index = 0

    while len(completion_times) < len(processes):
        while (
            next_process_index < len(processes)
            and int(processes[next_process_index]["arrival_time"]) <= current_time
        ):
            ready_queue.append(processes[next_process_index])
            next_process_index += 1

        if not ready_queue:
            next_arrival = int(processes[next_process_index]["arrival_time"])
            gantt.append(("IDLE", current_time, next_arrival))
            current_time = next_arrival
            continue

        process = ready_queue.popleft()
        pid = str(process["name"])
        run_time = min(quantum, remaining_times[pid])
        start = current_time
        current_time += run_time
        remaining_times[pid] -= run_time
        gantt.append((pid, start, current_time))

        while (
            next_process_index < len(processes)
            and int(processes[next_process_index]["arrival_time"]) <= current_time
        ):
            ready_queue.append(processes[next_process_index])
            next_process_index += 1

        if remaining_times[pid] > 0:
            ready_queue.append(process)
        else:
            completion_times[pid] = current_time

    rows = _rows_from_completion(processes, completion_times)
    return _finish(f"Round Robin (RR), Quantum = {quantum}", rows, gantt, "RR.csv")


if __name__ == "__main__":
    from pydantic import BaseModel, ConfigDict, Field

    class Process(BaseModel):
        name: str
        arrival_time: int = Field(..., alias="AT")
        burst_time: int = Field(..., alias="BT")
        priority: int = Field(..., alias="PR")

        model_config = ConfigDict(populate_by_name=True)

    class Processes(BaseModel):
        processes: list[Process]

    example_processes = Processes(
        processes=[
            Process(name="P1", AT=0, BT=5, PR=2),
            Process(name="P2", AT=1, BT=3, PR=1),
            Process(name="P3", AT=2, BT=1, PR=3),
        ]
    )

    FCFS(example_processes)
