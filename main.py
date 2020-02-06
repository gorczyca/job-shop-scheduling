import csv
import random
import time
import math
import argparse
import copy

from graphical_representation import draw_chart
from step import Step
from annealing import Annealing

random.seed(time.clock())

DEFAULT_ITERATIONS_NUMBER       = 50_000
DEFAULT_INITIAL_TEMPERATURE     = 50
DEFAULT_TEMPERATURE_UPDATE      = 'linear'
DEFAULT_FILE_NAME               = 'testdata/2/tai15x15_1.csv'  
DEFAULT_DECAY_CONSTANT          = 0.8
DEFAULT_GRADUAL_CONSTANT_A      = 30_000
DEFAULT_GRADUAL_CONSTANT_N      = 2

def get_cmd_arguments():
    """Parses commandline arguments and provides help when used in shell.

    Returns parsed arguments object.
    """
    parser = argparse.ArgumentParser(description='Job Shop Scheduling Problem Solver.')
    
    parser.add_argument('-fn', '--file_name', type=str, help=f'Input filename. Default {DEFAULT_FILE_NAME}', default=DEFAULT_FILE_NAME)
    parser.add_argument('-it', '--initial_temperature', type=int, help=f'Initial temperature value. Default {DEFAULT_INITIAL_TEMPERATURE}.', default=DEFAULT_INITIAL_TEMPERATURE)
    parser.add_argument('-tu', '--temperature_update', type=str, 
                        help=f'Update of temperature. Possible values: linear, decay, gradual, Default: {DEFAULT_TEMPERATURE_UPDATE}', default=DEFAULT_TEMPERATURE_UPDATE)
    parser.add_argument('-in', '--iterations_number', type=int, help=f'Number of iterations. Default {DEFAULT_ITERATIONS_NUMBER}.', default=DEFAULT_ITERATIONS_NUMBER)
    parser.add_argument('-dc', '--decay_constant', type=float, 
                        help=f'Decay constant. Relevant if "temperature_update"="decay". Default {DEFAULT_DECAY_CONSTANT}', default=DEFAULT_DECAY_CONSTANT)
    parser.add_argument('-gda', '--gradual_constant_a', type=int, 
                        help=f'Gradual constant a. Relevant if "temperature_update"="gradual". Default {DEFAULT_GRADUAL_CONSTANT_A}.', default=DEFAULT_GRADUAL_CONSTANT_A)
    parser.add_argument('-gcn', '--gradual_constant_n', type=float, 
                        help=f'Gradual constant n. Relevant if "temperature_update"="gradual". Default {DEFAULT_GRADUAL_CONSTANT_N}.', default=DEFAULT_GRADUAL_CONSTANT_N)

    return parser.parse_args()

def print_queues(queues):
    """Prints machine queues and max length.
    Format:
    M <machine_id>: <job_id>/<step_no>: <start>-<stop>, tb: <time_before>  
    """
    max_length = 0
    for machine_id, queue in enumerate(queues):
        print(f'M {machine_id}: ', end='')
        for step in queue:
            if step.stop > max_length:
                max_length = step.stop
            print(f'{step.job_id}/{step.step_no}: {step.start}-{step.stop}, tb:{step.time_before}  ', end = '')
        print('')

    print(f'Total length: {max_length}')

def get_total_length(queues):
    """Returns max (queue) length.
    """
    max_length = 0
    for queue in queues:
        for step in queue:
            if step.stop > max_length:
                max_length = step.stop
    return max_length

def print_jobs(jobs):
    """Prints jobs (used for comparison with the input file).
    Format:
    M: <machine_id> D: <duration>; <job_id>/<step_no>
    """
    for job in jobs:
        for step in job:
            print(f'M: {step.machine_id} D: {step.duration}; {step.job_id}/{step.step_no}\t', end='')
        print('')

def _contained(queue, step):
    """True if queue contains step.
    """
    for _step in queue:
        if step.job_id == _step.job_id and step.step_no == _step.step_no:
            return True
    return False

def initialize_queues(machines_no):
    """Initializes empty queues.
    Returns empty queues.
    """
    queues = []
    for i in range(machines_no):
        queues.append([])

    return queues

def find_step(queues, job_id, step_no):
    """Finds step in queues given job_id and step_no.
    Returns found step.
    """
    for queue in queues:
        for step in queue:
            if step.job_id == job_id and step.step_no == step_no:
                return step

def find_ending(queues, job_id):
    """Finds the timepoint when job with given job_id ends.
    Returns timepoint.
    """
    ending = 0
    for queue in queues:
        for step in queue:
            if step.job_id == job_id:
                if ending < step.stop:
                    ending = step.stop
    
    return ending

def random_step(queues, machines_no):
    """Returns random step from the queues.
    """
    machine_id = random.randint(0, machines_no - 1) # inclusive
    machineStepsNo = len(queues[machine_id])
    step_no = random.randint(0, machineStepsNo - 1)
    return machine_id, step_no

def read_csv(file_name, print_info=False):
    """Reads data from input file (style 1).
    Returns list of jobs, number of jobs, number of machines.
    """
    with open(file_name, newline='') as csv_file:
        reader = csv.reader(csv_file)    
        dimensions = next(reader)[0].split()
        jobs_no = int(dimensions[0])
        machines_no = int(dimensions[1])
        jobs = []
        for job_id, row in enumerate(reader):
            row = row[0].split()
            jobs.append([]) 

            # number of steps matches number of machines
            for i in range(machines_no):
                machine_id = int(row[2 * (i+1) - 2])
                duration = int(row[2 * (i+1) - 1])
                step = Step(job_id, i, machine_id, duration)
                jobs[job_id].append(step) 
        
        if print_info:
            print_jobs(jobs)

        return jobs, jobs_no, machines_no

def read_csv_2(file_name, print_info=False):
    """Reads data from input file (style 1).
    Returns list of jobs, number of jobs, number of machines.
    """
    with open(file_name, newline='') as csv_file:
        reader = csv.reader(csv_file)    
        dimensions = next(reader)[0].split()
        jobs_no = int(dimensions[0])
        machines_no = int(dimensions[1])
        # skip the 'Times' string
        next(reader)
        jobs = []

        for job_id in range(jobs_no):
            jobs.append([])
            job_times = next(reader)[0].split()
            
            for step_no, job_time in enumerate(job_times):
                step = Step(job_id, step_no, math.inf, int(job_time))
                jobs[job_id].append(step)

        # skip the 'Machines' string 
        next(reader)
        for job_id in range(jobs_no):
            job_machines = next(reader)[0].split()

            for step_no, step_machine_id in enumerate(job_machines):
                jobs[job_id][step_no].machine_id = int(step_machine_id) - 1 # cause they are encoded from 1
        
        if print_info:
            print_jobs(jobs)

        return jobs, jobs_no, machines_no

def fill_machine_queues(jobs, queues, single_time_unit_width=0):
    """Fills the queues with the remaining steps.
    Queues can be already containing some steps. Only those who are not already in queues are added.
    Returns queues filled with all the jobs.
    """
    # queues can be already filled partially
    for job in jobs:
        for step in job:
            
            # if it's already contained, don't consider it anymore
            if _contained(queues[step.machine_id], step):
                continue            
            
            step_copy = step.copy()

            squeezed = False
            job_ending = find_ending(queues, step_copy.job_id)

            # the previous step of the job ended before the machine is free
            # try to squeeze it
            for count, _step in enumerate(queues[step.machine_id]):
                if _step.start > job_ending:
                    # take the first that starts after job ending
                    if _step.time_before >= step_copy.duration: 
                        # if there is enough space
                        if _step.start - step_copy.duration >= job_ending:
                            # it is possible to squeeze

                            squeezed = True

                            if count == 0:
                                step_copy.start = job_ending
                                step_copy.time_before = job_ending
                            else:                        
                                _previous_step = queues[step.machine_id][count - 1]
                                if _previous_step.stop >= job_ending:
                                    step_copy.start = _previous_step.stop
                                    step_copy.time_before = 0
                                else:
                                    step_copy.start = job_ending
                                    step_copy.time_before = step_copy.start - _previous_step.stop

                            step_copy.stop = step_copy.start + step_copy.duration
                            _step.time_before = _step.start - step_copy.stop # TODO: tu powinny być kopie więc powinienem móc na czillu updateowac
                            queues[step.machine_id].insert(count, step_copy)
                            break            

            if not squeezed:
                # if the machine queue is empty
                #           or
                # if it is free when the previous job ends
                # or it failed to squeeze
                if not queues[step_copy.machine_id]:
                    step_copy.start = job_ending
                    step_copy.time_before = job_ending
                else: 
                    if queues[step_copy.machine_id][-1].stop <= job_ending:
                        step_copy.start = job_ending
                        step_copy.time_before = job_ending - queues[step_copy.machine_id][-1].stop
                    else:
                        step_copy.start = queues[step_copy.machine_id][-1].stop
                        step_copy.time_before = 0

                step_copy.stop = step_copy.start + step_copy.duration
                queues[step.machine_id].append(step_copy)

    return queues

def generate_neighbour(queues, machines_no, jobs, single_time_unit_width=0):
    """Generates neighbour given schedule.
    Returns neighbour (neighbouring solution).
    """

    machine_id, step_no = random_step(queues, machines_no)

    # move it as much to the left as possible
    step = queues[machine_id][step_no]    
    new_queues = initialize_queues(machines_no)

    if step.step_no == 0:
        # if this is the first step to do, just put it on the beginning
        new_step = step.copy()
        new_step.time_before = 0
        new_step.start = 0
        new_step.stop = new_step.start + new_step.duration
        new_queues[machine_id].append(new_step)

    else: 
        previous_step = find_step(queues, step.job_id, step.step_no - 1)

        # preserve all the steps that end maximally at the time previous_step.stop
        for _machine_id, queue in enumerate(queues):
            for _step in queue:
                if _step.stop <= previous_step.stop:
                    new_queues[_machine_id].append(_step.copy())

        machine_ending = 0
        if new_queues[machine_id]:
            machine_ending = new_queues[machine_id][-1].stop

        # put step right when the previous is finished
        step_copy = step.copy()
        step_copy.start = previous_step.stop
        step_copy.time_before = step_copy.start - machine_ending
        step_copy.stop = step_copy.start + step_copy.duration

        new_queues[machine_id].append(step_copy)

        new_queues_length = get_total_length(new_queues)
        final_queues_length = get_total_length(queues)

    return fill_machine_queues(jobs, new_queues, single_time_unit_width=single_time_unit_width)


if __name__ == '__main__':

    jobs = []
    jobs_no = 0
    machines_no = 0

    args = get_cmd_arguments()

    annealing = Annealing(initial_temperature=args.initial_temperature, 
                            temperature_update=args.temperature_update, 
                            iterations_number=args.iterations_number, 
                            decay_constant=args.decay_constant, 
                            gradual_constant_a=args.gradual_constant_a, 
                            gradual_constant_n=args.gradual_constant_n)

    if args.file_name.split('/')[1] == '1':
        jobs, jobs_no, machines_no = read_csv(args.file_name)
    else:
        jobs, jobs_no, machines_no = read_csv_2(args.file_name)


    initial_queues = initialize_queues(machines_no)

    queues = fill_machine_queues(jobs, initial_queues)
    length = get_total_length(queues)
    single_time_unit_width = draw_chart(queues, machines_no, jobs_no, length, 
                                        name=f'Initial schedule - Length = {length}')

    print(f'Initial length: {length}')

    for step in range(args.iterations_number):

        new_queues = generate_neighbour(queues, machines_no, jobs, single_time_unit_width=single_time_unit_width)
     
        new_length = get_total_length(new_queues)
      
        if length > new_length:
            print(f'A better solution found with length: {new_length}\r')
            length = new_length
            queues = new_queues

        elif new_length > length: 

            probability = annealing.calculate_probability(length, new_length)
            if probability > random.random():
                # also accept it                
                print(f'Accepted worse solution with the probability of {probability}\r')
                print(f'New length is: {new_length}\r')

                queues = new_queues
                length = new_length

        annealing.update_iteration()
        print(f'{step} of {args.iterations_number}', end='\r', flush=True)
    
    print('Simulation ended.')
    print(f'Final length is: {length}')

    # print_queues(queues)
    draw_chart(queues, machines_no, jobs_no, length, name=f'Final schedule - Length = {length}', single_time_unit_width=single_time_unit_width)
