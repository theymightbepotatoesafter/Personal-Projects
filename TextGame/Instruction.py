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

    def __init__(self, identifier: str, data: Any):
        self.data = data
        self.id = identifier

    def get_id(self):
        return self.id

    def get_data(self):
        return self.data

displayID = [   'initializeDisplay', 
                'changeDisplaySize', 
                'updateDisplay', 
                'updateFrameBuffer',
                'resetDisplay'
            ]

class DisplayInstruction(Instruction):

    def __init__(self, identifier: str, display_num: int = 0, data: Any = None, *args, **kwargs):
        super().__init__(identifier, data)
        self.to = display_num
        self.args = args
        self.kwargs = kwargs

class DataRequest(Instruction):

    def __init__(self, requestee: int, requester, requested, data = None):
        self.to = requestee
        self.give = requester
        self.id = requested
        self.data = data

    def load_data(self, data):
        self.data = data

    def unload_data(self):
        return super().get_data()

class InstructionDecoder:

    def __init__(self, identifier: str):
        self.id = identifier
