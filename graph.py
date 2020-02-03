from graphics import *

colors = [  'white',    # 1
            'red',      # 2
            'yellow',   # 3
            'blue',     # 4
            'pink',     # 5
            'purple',   # 6 
            'green',    # 7     
            'magenta',  # 8 
            'cyan',     # 9
            'chocolate',   # 10
            'brown',    # 11
            'grey',     # 12
            'orange',   # 13
            'gold',     # 14
            'silver',    # 15
            'greenyellow',
            'darkkhaki',
            'firebrick',
            'darkcyan',
            'coral',
            'indigo'

]


def draw_chart(queues, machinesNo, jobsNo, length, labels=False, single_time_unit_width=0):
    WINDOW_DIM_X = 1920
    WINDOW_DIM_Y = 1080

    TRANSPARENT = 'black'

    machine_height = WINDOW_DIM_Y / (machinesNo + 2)

    if single_time_unit_width == 0:
        single_time_unit_width = (WINDOW_DIM_X - (2 * machine_height)) / length 
    
    win = GraphWin('Rectangle', WINDOW_DIM_X, WINDOW_DIM_Y)
    win.setBackground(TRANSPARENT)

    machine_label_x = machine_height / 2

    for machineId, machine in enumerate(queues):
        previous_step_end = machine_height # initial value
        
        starting_point_top = (machineId * machine_height) + machine_height
        ending_point_bottom = starting_point_top + machine_height
        machine_label_y = (ending_point_bottom + starting_point_top) / 2
        
        machine_label = Text(Point(machine_label_x, machine_label_y), f'M {machineId}')
        machine_label.setTextColor('white')
        machine_label.setSize(30)

        machine_label.draw(win)



        for step in machine:

            
            if step.timeBefore > 0:
                black_rect_width = step.timeBefore * single_time_unit_width
                next_step_end = previous_step_end + black_rect_width
                black_rect = Rectangle(Point(previous_step_end, starting_point_top), 
                                        Point(next_step_end, ending_point_bottom))
                black_rect.setFill(TRANSPARENT)
                black_rect.draw(win)
                previous_step_end = next_step_end
            
            rect_width = step.duration * single_time_unit_width
            next_step_end = previous_step_end + rect_width
            rect = Rectangle(Point(previous_step_end, starting_point_top),
                                Point(next_step_end, ending_point_bottom))
            rect.setFill(colors[step.jobId])
            rect.draw(win)

            label = Text(rect.getCenter(), f'{step.jobId}/{step.stepNo}')
            label.setSize(30)
            label.setTextColor('black')
            label.draw(win)

            previous_step_end = next_step_end

    win.getMouse()
    win.close()

    return single_time_unit_width