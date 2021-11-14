"""
Being

Version : v0.1
Author  : Christian Carter
Date    : 10/11/21

Base classes for beings within the world
"""

import logging
import random
from math import exp
from Entity import *

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

class Race:
    def __init__(self, offset : float):
        self.base_health = 100 + (offset * exp(-1 * (random.uniform(-0.5, 2))))
        self.base_magica = 100 + (offset * exp(-1 * (random.uniform(-0.5, 2))))
        self.base_defend = 0.50 + (0.01 * offset * exp(-1 * (random.uniform(-0.5, 2))))
        self.base_attack = 10 + (0.1 * offset * exp(-1 * (random.uniform(-0.5, 2))))

class Human(Race):
    def __init__(self, startLevel : int):
        super().__init__(10)
        self.level = startLevel

    def level_up(self):
        self.level += 1
        self.base_attack += ((0.5 * self.level) + 1)
        self.base_magica += ((0.43 * self.level) + 0.75)
        self.base_health += ((0.75 * self.level) + 5)
        self.base_defend += ((0.07 * self.level))

    def __str__(self) -> str:
        return f"Health: {self.base_health}\nMagica: {self.base_magica}\nDefence: {self.base_defend}\nAttack{self.base_attack}"

