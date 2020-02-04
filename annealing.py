"""Annealing class.

Used to perform every simulated-annealing task.
"""

import math

class Annealing:
    def __init__(self, initial_temperature=10, temperature_update='linear',
                iterations_number=100_000, decay_constant=0.5,
                gradual_constant_a=1000, gradual_constant_n=2):
        self.__initial_temperature = initial_temperature
        self.__iterations_number = iterations_number
        self.__current_iteration = 0
        self.__decay_constant=decay_constant
        self.__gradual_constant_a = gradual_constant_a
        self.__gradual_constant_n = gradual_constant_n
        self.__min_temperature = initial_temperature / iterations_number
        self.__temperature_update = temperature_update
        self.__temperature_update_switcher = {
            'linear'    : self.__linear_temperature_update,
            'decay'     : self.__decay_temperature_update,
            'gradual'   : self.__gradual_temperature_update
        }

    def __calculate_temperature(self):
        """Returns the current temperature, using predefined temperature update option.
        """
        update = self.__temperature_update_switcher.get(self.__temperature_update, lambda: 'Error')
        return max(self.__min_temperature, update())
        
    def __linear_temperature_update(self):
        """Updates the temperature in the linear way.
        """
        fraction = self.__current_iteration / self.__iterations_number
        subtractedTemperature = fraction * self.__initial_temperature
        return self.__initial_temperature - subtractedTemperature
        
    def __decay_temperature_update(self): 
        """Updates the temperature in the decay way.
        """
        decay_coefficient = self.__decay_constant ** self.__current_iteration
        return decay_coefficient * self.__initial_temperature
        
    def __gradual_temperature_update(self):
        """Updates the temperature in the gradual way.
        """
        gradual_coefficient = 1 - (self.__current_iteration / self.__gradual_constant_a) * self.__gradual_constant_n
        return gradual_coefficient * self.__initial_temperature

    def calculate_probability(self, length, new_length):
        """Calculates probability based on the current temperature, length and new_length. 
        """
        temperature = self.__calculate_temperature()
        return math.exp(-(new_length - length)/temperature)

    def update_iteration(self):
        """Increases the iteration counter by 1 after each iteration.
        """
        self.__current_iteration += 1