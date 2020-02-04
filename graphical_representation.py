"""Graphical representation.

Provides the graphical representation of given solution.
"""

from graphics import *

WINDOW_DIM_X = 1920
WINDOW_DIM_Y = 1080

FONT_SIZE = 20

TRANSPARENT = 'black'
MACHINE_LABEL_COLOUR = 'white'
STEP_LABEL_COLOUR = 'black'

COLORS = [  'white',        # 1
            'red',          # 2
            'yellow',       # 3
            'blue',         # 4
            'pink',         # 5
            'purple',       # 6 
            'green',        # 7     
            'magenta',      # 8 
            'cyan',         # 9
            'chocolate',    # 10
            'brown',        # 11
            'grey',         # 12
            'orange',       # 13
            'gold',         # 14
            'silver',       # 15
            'greenyellow',  # 16
            'darkkhaki',    # 17
            'firebrick',    # 18
            'darkcyan',     # 19
            'coral',        # 20
            'indigo'        # 21
]

def draw_chart(queues, machines_no, jobs_no, length, labels=False, single_time_unit_width=0, name=''):
    """Draws chart as the graphical interpretation.
    """
    machine_height = WINDOW_DIM_Y / (machines_no + 2)

    if single_time_unit_width == 0:
        single_time_unit_width = (WINDOW_DIM_X - (2 * machine_height)) / length 
    
    win = GraphWin(name, WINDOW_DIM_X, WINDOW_DIM_Y)
    win.setBackground(TRANSPARENT)

    machine_label_x = machine_height / 2

    for machine_id, machine in enumerate(queues):
        previous_step_end = machine_height # initial value
        
        starting_point_top = (machine_id * machine_height) + machine_height
        ending_point_bottom = starting_point_top + machine_height
        machine_label_y = (ending_point_bottom + starting_point_top) / 2
        
        machine_label = Text(Point(machine_label_x, machine_label_y), f'M {machine_id}')
        machine_label.setTextColor(MACHINE_LABEL_COLOUR)
        machine_label.setSize(FONT_SIZE)

        machine_label.draw(win)

        for step in machine:            
            if step.time_before > 0:
                black_rect_width = step.time_before * single_time_unit_width
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
            rect.setFill(COLORS[step.job_id])
            rect.draw(win)

            label = Text(rect.getCenter(), f'{step.job_id}/{step.step_no}')
            label.setSize(FONT_SIZE)
            label.setTextColor(STEP_LABEL_COLOUR)
            label.draw(win)

            previous_step_end = next_step_end

    win.getMouse()
    win.close()

    return single_time_unit_width