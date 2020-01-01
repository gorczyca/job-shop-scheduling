import csv

from step import Step

# FILENAME = 'abz5.csv'
FILENAME = 'example.csv'

def readCsv(fileName):
    with open(fileName, newline='') as csvFile:
        reader = csv.reader(csvFile, delimiter=' ')    
        dimensions = next(reader)
        jobsNo = int(dimensions[0])
        machinesNo = int(dimensions[1])
        jobs = []
        steps = []
        for jobId, row in enumerate(reader):
            jobs.append([]) # unnecessary
            # number of steps matches number of machines
            for i in range(machinesNo):
                machineId = int(row[2 * (i+1) - 2])
                duration = int(row[2 * (i+1) - 1])
                step = Step(jobId, i, machineId, duration)
                jobs[jobId].append(step) # unnecessary
                steps.append(step)
        
        # for job in jobs:
        #     for step in job:
        #         print(f'{step.machineId}/{step.duration}  ', end='')
        #     print('')

        return steps, machinesNo

def getOverallLength(endings):
    return max(endings)

def fillQueues(queues, endings, steps):
    for step in steps:
        machineId = step.machineId
        jobId = step.jobId
        lastJobStepEnding = endings[jobId]
        # todo: timeBefore

        squeezed = False
        for count, machineStep in enumerate(queues[machineId]):
            if machineStep.start > lastJobStepEnding:
                # if there is time before, squeeze it in
                if machineStep.timeBefore >= step.duration: # if there is enough space
                    if machineStep.start - step.duration >= lastJobStepEnding: # jeżeli mozna wpisać w ten slot tak by nie zaburzyć reszty
                        if count == 0:
                            step.start = 0
                        else:                        
                            previousMachineStep = queues[machineId][count - 1]
                            if previousMachineStep.stop >= lastJobStepEnding:
                                step.start = previousMachineStep.stop
                            else:
                                step.start = lastJobStepEnding

                        step.stop = step.start + step.duration
                        endings[jobId] = step.stop
                        step.timeBefore = 0
                        machineStep.timeBefore = machineStep.start - step.stop
                        queues[machineId].insert(count, step)
                        
                        squeezed = True
                        break

        if not squeezed:
            if not queues[machineId]:      # if queue doesn't contain any steps
                step.start = lastJobStepEnding
                step.timeBefore = step.start
            else:
                lastStep = queues[machineId][-1]  # take last element of the machine queue
                if lastJobStepEnding <= lastStep.stop:
                    step.start = lastStep.stop
                else: 
                    step.start = lastJobStepEnding
                step.timeBefore = step.start - lastStep.stop

            stepEnd = step.start + step.duration
            step.stop = stepEnd
            endings[jobId] = stepEnd
            queues[machineId].append(step)

    for queue in queues:
        for step in queue:
            print(f'{step.jobId}/{step.stepNo}: {step.start}-{step.stop}, tb:{step.timeBefore}  ', end = '')
        print('')

    length = getOverallLength(endings)
    print(f'Total length: {length}')




if __name__ == '__main__':
    steps, machinesNo = readCsv(FILENAME)
    queues = []
    endings = [] # indicates, when the last step of a job ends 
    for i in range(machinesNo):
        queues.append([])
        endings.append(0)
    queues = fillQueues(queues, endings, steps)
