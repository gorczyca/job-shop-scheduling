"""Step class.

Used to represent single step of given operation.
"""
from math import inf as UNKNOWN

class Step:
    def __init__(self, job_id, step_no, machine_id, duration, start=UNKNOWN, stop=UNKNOWN, time_before=UNKNOWN):
        self.job_id = job_id
        self.step_no = step_no
        self.machine_id = machine_id
        self.duration = duration
        self.start = start
        self.stop = stop
        self.time_before = time_before

    def copy(self):
        return Step(self.job_id, self.step_no, self.machine_id, self.duration,                     
                    start=self.start, stop=self.stop, time_before=self.time_before)

        
