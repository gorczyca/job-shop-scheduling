"""Step class.

Used to represent single step of given operation.
"""
from math import inf as UNKNOWN

class Step:
    def __init__(self, jobId, stepNo, machineId, duration, start=UNKNOWN, stop=UNKNOWN, timeBefore=UNKNOWN):
        self.jobId = jobId
        self.stepNo = stepNo
        self.machineId = machineId
        self.duration = duration
        self.start = start
        self.stop = stop
        self.timeBefore = timeBefore
        
