import math

UNKNOWN = math.inf

class Step:
    def __init__(self, jobId, stepNo, machineId, duration, start=UNKNOWN, stop=UNKNOWN, freeTimeBefore=UNKNOWN):
        self.jobId = jobId
        self.stepNo = stepNo
        self.machineId = machineId
        self.duration = duration
        self.start = start
        self.stop = stop
        
