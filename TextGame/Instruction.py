"""
Instruction Set v0.2

Author  : Christian Carter
Date    : 19 Aug 2021

Code for the instruction set that packages the input
screen information to the game engine to be displayed
"""

version_info = "v0.2"
import logging
from typing import Any, List, Dict
import pickle

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

class Instruction(object):

    def __init__(self):
        raise NotImplementedError("This is a base class and should not be called")

class testInstruction(Instruction):

    def __init__(self, data: Any):
        self.data = data