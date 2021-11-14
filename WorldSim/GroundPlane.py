"""
Ground Plane

Version : v0.1
Author  : Christian Carter
Date    : 12 Nov 2021

Base classes for ground plane for entities to move around on. Several levels will be
utilized to minimize the computing power needed
"""

import logging
from typing import List, Tuple
from Entity import *

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

class Ground():
    
    def __init__(self, size : Tuple[int, int], scales : List, max_entities : List):
        """
            size should be in total meters
        """    
        self.x, self.y = size    # x, y
        self.scale = scales
        self.max = max_entities
        self.entities = EntityContainer('ground', 1205)
        self.grid = []
        for row in range(self.y):
            new_row = []
            for col in range(self.x):
                new_row.append(" ")
            self.grid.append(new_row)
        self.__position_lists()
        self.set_position()
        self.set_scale(0)

    def __position_lists(self, ):
        self.position = {}
        for scale in range(len(self.scale)):
            self.position[scale] = [int(self.x / self.scale[scale]), int(self.y / self.scale[scale])]

    def __str__(self):
        return str(self.grid)

    def set_scale(self, scale_index):
        self.scale_index = scale_index

    def set_position(self, position : Tuple[int, int] = [0, 0]):
        self.scale_pos = position

    def render(self):
        try:
            assert(self.scale)
        except AssertionError:
            print('Please choose a scale before continuing')
            return
            
        log.debug(self.scale)
        log.debug(self.scale_index)
        x_pos = self.scale[self.scale_index] * self.scale_pos[0]
        y_pos = self.scale[self.scale_index] * self.scale_pos[1]
        log.debug(x_pos)
        log.debug(y_pos)
        for row in range(y_pos, y_pos + self.scale[self.scale_index]):
            print(self.grid[row][x_pos:(x_pos + self.scale[self.scale_index])])

if __name__ == "__main__":
    scales = [5, 10,25, 50, 100]
    entity_scales = [20, 20, 20, 20, 20]
    ground = Ground((100,100), scales, 20)
    print(ground.position)
    ground.set_scale(1)
    ground.set_position((2, 5))
    ground.render()
    
