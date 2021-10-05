"""
Instruction v0.4

Author  : Christian Carter
Date    : 30 Sep, 2021

Instructions to be sent to and from the game engine
"""
version_info = 'v0.4'

from typing import Any

class Instruction(object):

    def __init__(self, task: str, args: Any = None, to: str = 'displayEngine'):
        self.to = to
        self.task = task
        self.args = args
    
    def __repr__(self) -> str:
        return f'Instruction(task: {self.task}, arguments: {self.args}, destination: {self.to})'

    def set_destination(self, destination):
        self.to = destination
    
    def destination(self) -> str:
        return self.to

    def get_task(self) -> str:
        return self.task

    def set_task(self, task):
        self.task = task

    def get_args(self):
        return self.args

    def set_args(self, args):
        self.args = args
