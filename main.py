import csv
import random
import time
import math
import argparse

from graph import draw_chart

from step import Step
from annealing import Annealing

# TODO: commandline arguments (Done)
# TODO: other input representation to compare (DONE?)
# TODO: neighbour function
# TODO: temperature initialization, updation etc
# TODO: graphic representation
# TODO: github (readme) etc

random.seed(time.clock())

DEFAULT_FILENAME = 'testdata/1/abz5.csv'

def get_cmd_arguments():

    parser = argparse.ArgumentParser(description='Job Shop Scheduling Problem Solver.')
    
    parser.add_argument('-fn', '--file_name', type=str, help='Input filename.', default=DEFAULT_FILENAME)
    parser.add_argument('-it', '--initial_temperature', type=int, help='Initial temperature value. Default 10.', default=10)
    parser.add_argument('-tu', '--temperature_update', type=str, 
                        help='Update of temperature. Possible values: linear, decay, gradual, Default: linear', default='linear')
    parser.add_argument('-in', '--iterations_number', type=int, help='Number of iterations. Default 100_000.', default=100_000)
    parser.add_argument('-dc', '--decay_constant', type=float, 
                        help='Decay constant. Relevant if "temperature_update"="decay". Default 0.5', default=0.5)
    parser.add_argument('-gda', '--gradual_constant_a', type=int, 
                        help='Gradual constant a. Relevant if "temperature_update"="gradual". Default 1000.', default=1000)
    parser.add_argument('-gcn', '--gradual_constant_n', type=float, 
                        help='Gradual constant n. Relevant if "temperature_update"="gradual". Default 2.', default=2)

    return parser.parse_args()

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

def fillMachineQueues(jobs, queues, single_time_unit_width=0, draw=False):
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
            if draw:
                length = _getTotalLength(queues)
                draw_chart(queues, machinesNo, jobsNo, length, single_time_unit_width=single_time_unit_width)

    return queues

def generateNeighbour(queues, machinesNo, jobs, printInfo=False, single_time_unit_width=0):
    # move it as much to the left as possible
    machineId, stepNo = _randomStep(queues, machinesNo)

    print(f'Trying to push M: {machineId}, StepNo: {stepNo}')

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

        # draw_chart(newQueues, machinesNo, jobsNo, length, single_time_unit_width=single_time_unit_width)

    return fillMachineQueues(jobs, newQueues, single_time_unit_width=single_time_unit_width, draw=False)


if __name__ == '__main__':

    jobs = []
    jobsNo = 0
    machinesNo = 0

    args = get_cmd_arguments()

    annealing = Annealing(initial_temperature=args.initial_temperature, 
                            temperature_update=args.temperature_update, 
                            iterations_number=args.iterations_number, 
                            decay_constant=args.decay_constant, 
                            gradual_constant_a=args.gradual_constant_a, 
                            gradual_constant_n=args.gradual_constant_n)

    if args.file_name.split('/')[1] == '1':
        jobs, jobsNo, machinesNo = readCsv(args.file_name)
    else:
        jobs, jobsNo, machinesNo = readCsv2(args.file_name)


    initialQueues = _initializeQueues(machinesNo)

    queues = fillMachineQueues(jobs, initialQueues)
    length = _getTotalLength(queues)
    # _printQueues(queues)
    single_time_unit_width = draw_chart(queues, machinesNo, jobsNo, length)



    print(f'Initial length: {length}')

    for step in range(args.iterations_number):

        newQueues = generateNeighbour(queues, machinesNo, jobs, printInfo=True, single_time_unit_width=single_time_unit_width)
        newLength = _getTotalLength(newQueues)

        if newLength <= length :
            # if current solution is better, accept it
            queues = newQueues
            if length > newLength:
                print(f'A better solution found with length: {newLength}\r')
                # TODO: temporary
                draw_chart(queues, machinesNo, jobsNo, length, single_time_unit_width=single_time_unit_width)

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

                 # TODO: temporary
                draw_chart(queues, machinesNo, jobsNo, length, single_time_unit_width=single_time_unit_width)

        annealing.update_iteration()
        print(f'{step} of {args.iterations_number}', end='\r', flush=True)
    print('Simulation ended.')
    print(f'Final length is: {length}')
    
    draw_chart(queues, machinesNo, jobsNo, length, single_time_unit_width=single_time_unit_width)

