import csv
import random
import time
import math

from step import Step
from annealing import Annealing

# TODO: commandline arguments
# TODO: other input representation to compare
# TODO: neighbour function
# TODO: temperature initialization, updation etc
# TODO: graphic representation
# TODO: github (readme) etc

# FILENAME = 'testdata/abz7.csv'
FILENAME = 'testdata2/tai15x15_1.csv'

ITERATIONS = 100_000

# FILENAME = 'abz5.csv'
# FILENAME = 'example.csv'
# FILENAME = 'turboeasy.csv'

random.seed(time.clock())

def _printQueues(queues):
    maxLength = 0
    for queue in queues:
        for step in queue:
            if step.stop > maxLength:
                maxLength = step.stop
            print(f'{step.jobId}/{step.stepNo}: {step.start}-{step.stop}, tb:{step.timeBefore}  ', end = '')
        print('')

    print(f'Total length: {maxLength}')

def _getTotalLength(queues):
    maxLength = 0
    for queue in queues:
        for step in queue:
            if step.stop > maxLength:
                maxLength = step.stop
    return maxLength

def _printJobs(jobs):
    for job in jobs:
        for step in job:
            print(f'M: {step.machineId} D: {step.duration}; {step.jobId}/{step.stepNo}\t', end='')
        print('')

def _contained(queue, step):
    for _step in queue:
        if step.jobId == _step.jobId and step.stepNo == _step.stepNo:
            return True
    return False

def _initializeQueues(machinesNo):
    queues = []
    for i in range(machinesNo):
        queues.append([])

    return queues

def _findStep(queues, jobId, stepNo):
    for queue in queues:
        for step in queue:
            if step.jobId == jobId and step.stepNo == stepNo:
                return step

def _findEnding(queues, jobId):
    ending = 0
    for queue in queues:
        for step in queue:
            if step.jobId == jobId:
                if ending < step.stop:
                    ending = step.stop
    
    return ending

def _randomStep(queues, machinesNo):
    machineId = random.randint(0, machinesNo - 1) # inclusive
    machineStepsNo = len(queues[machineId])
    stepNo = random.randint(0, machineStepsNo - 1)
    return machineId, stepNo

def readCsv(fileName, printInfo=False):
    with open(fileName, newline='') as csvFile:
        reader = csv.reader(csvFile)    
        dimensions = next(reader)[0].split()
        jobsNo = int(dimensions[0])
        machinesNo = int(dimensions[1])
        jobs = []
        for jobId, row in enumerate(reader):
            row = row[0].split()
            jobs.append([]) 

            # number of steps matches number of machines
            for i in range(machinesNo):
                machineId = int(row[2 * (i+1) - 2])
                duration = int(row[2 * (i+1) - 1])
                step = Step(jobId, i, machineId, duration)
                jobs[jobId].append(step) 
        
        if printInfo:
            _printJobs(jobs)

        return jobs, jobsNo, machinesNo

def readCsv2(fileName, printInfo=False):
    with open(fileName, newline='') as csvFile:
        reader = csv.reader(csvFile)    
        dimensions = next(reader)[0].split()
        jobsNo = int(dimensions[0])
        machinesNo = int(dimensions[1])
        # skip the 'Times' string
        next(reader)
        jobs = []

        for jobId in range(jobsNo):
            jobs.append([])
            jobTimes = next(reader)[0].split()
            
            for stepNo, jobTime in enumerate(jobTimes):
                step = Step(jobId, stepNo, math.inf, int(jobTime))
                jobs[jobId].append(step)

        # skip the 'Machines' string 
        next(reader)
        for jobId in range(jobsNo):
            jobMachines = next(reader)[0].split()

            for stepNo, stepMachineId in enumerate(jobMachines):
                jobs[jobId][stepNo].machineId = int(stepMachineId) - 1 # cause they are encoded from 1
        
        if printInfo:
            _printJobs(jobs)

        return jobs, jobsNo, machinesNo

def fillMachineQueues(jobs, queues):
    # queues can be already filled partially
    for job in jobs:
        for step in job:
            
            # if it's already contained, don't consider it anymore
            # print(f'MACHINE ID: {step.machineId}')
            # print(f'QUEUES LENGTH: {len(queues)}')
            if _contained(queues[step.machineId], step):
                continue            
            
            squeezed = False
            jobEnding = _findEnding(queues, step.jobId)

            # the previous step of the job ended before the machine is free
            # try to squeeze it
            ##### trying to squeeze ####
            for count, _step in enumerate(queues[step.machineId]):
                if _step.start > jobEnding:
                    # take the first that starts after job ending
                    if _step.timeBefore >= step.duration: 
                        # if there is enough space
                        if _step.start - step.duration >= jobEnding:
                            # it is possible to squeeze

                            squeezed = True

                            if count == 0:
                                step.start = jobEnding
                                step.timeBefore = jobEnding
                            else:                        
                                _previousStep = queues[step.machineId][count - 1]
                                if _previousStep.stop >= jobEnding:
                                    step.start = _previousStep.stop
                                    step.timeBefore = 0
                                else:
                                    step.start = jobEnding
                                    step.timeBefore = step.start - _previousStep.stop

                            step.stop = step.start + step.duration
                            _step.timeBefore = _step.start - step.stop
                            queues[step.machineId].insert(count, step)
                            break            

            if not squeezed:
                # if the machine queue is empty
                #           or
                # if it is free when the previous job ends
                # or it failed to squeeze
                if not queues[step.machineId]:
                    step.start = jobEnding
                    step.timeBefore = jobEnding
                else: 
                    if queues[step.machineId][-1].stop <= jobEnding:
                        step.start = jobEnding
                        step.timeBefore = jobEnding - queues[step.machineId][-1].stop
                    else:
                        step.start = queues[step.machineId][-1].stop
                        step.timeBefore = 0

                step.stop = step.start + step.duration
                queues[step.machineId].append(step)

    return queues

def generateNeighbour(queues, machinesNo, jobs, printInfo=False):
    # move it as much to the left as possible
    machineId, stepNo = _randomStep(queues, machinesNo)

    step = queues[machineId][stepNo]
    
    newQueues = _initializeQueues(machinesNo)

    if step.stepNo == 0:
        # if this is the first step to do, just put it on the beginning
        step.timeBefore = 0
        step.start = 0
        step.stop = step.start + step.duration
        newQueues[machineId].append(step)

    else: 
        previousStep = _findStep(queues, step.jobId, step.stepNo - 1)
        machineEnding = 0
        # preserve all the steps that end maximally at the time previousStep.stop
        for _machineId, queue in enumerate(queues):
            for _step in queue:
                if _step.stop <= previousStep.stop:
                    newQueues[_machineId].append(_step)

                    # save the ending on this machine
                    if _machineId == machineId:
                        if machineEnding < _step.stop:
                            machineEnding = _step.stop
        
        # put step right when the previous is finished
        step.start = previousStep.stop
        step.timeBefore = previousStep.stop - machineEnding
        step.stop = step.start + step.duration

        newQueues[machineId].append(step)
    
    return fillMachineQueues(jobs, newQueues)


if __name__ == '__main__':

    # jobs, jobsNo, machinesNo = readCsv(FILENAME)
    jobs, jobsNo, machinesNo = readCsv2(FILENAME, printInfo=True)

    initialQueues = _initializeQueues(machinesNo)

    queues = fillMachineQueues(jobs, initialQueues)
    length = _getTotalLength(queues)
    _printQueues(queues)

    annealing = Annealing()

    print(f'Initial length: {length}')

    for step in range(ITERATIONS):

        newQueues = generateNeighbour(queues, machinesNo, jobs, printInfo=True)
        newLength = _getTotalLength(newQueues)

        if newLength <= length :
            # if current solution is better, accept it
            queues = newQueues
            if length > newLength:
                print(f'A better solution found with length: {newLength}\r')

            length = newLength
        else:

            # accept the solution, based on probability
            probability = annealing.calculate_probability(length, newLength)
            if probability > random.random():
                # also accept it
                
                print(f'Accepted worse solution with the probability of {probability}\r')
                print(f'New length is: {newLength}\r')

                queues = newQueues
                length = newLength

        annealing.update_iteration()
        print(f'{step} of {ITERATIONS}', end='\r', flush=True)
    print('Simulation ended.')
    print(f'Final length is: {length}')
