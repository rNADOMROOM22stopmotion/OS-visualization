from queue import Queue
from pydantic import BaseModel


class Process(BaseModel):
    pid: int
    at: float  # arrival time
    bt: float  # burst time
    ct: float  # completion time
    tat: float  # turn-around-time
    wt: float  # wait time
    rt: float  # real time

class RoundRobin():
    def __init__(self, processes: list[Process]):
        self.Processes = processes

    def run(self):
        ready_queue = Queue(maxsize=len(self.Processes))





