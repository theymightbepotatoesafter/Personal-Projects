"""
Game Engine v0.3

Author  : Christian Carter
Date    : 18 Aug 2021

Code for mkaing all of the other code talk to eachother.
"""
version_info = "v0.3"
import os
import time
import logging
from typing import List, Tuple
from Instruction import *
from Display import *
#from InputScreen import *
from multiprocessing.connection import Client, Connection, wait

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

class GameInstance():

    def __init__(self, screen_size: Tuple[int, int], max_displays: int = 3):
        """
            A GameInstance object is the backbone of the game.
            It routs Instruction objects to and from the Input
            and Output cmdDisplay objects. It essentially funcitons
            as the hardware the game is played on.
        """
        self.__path = os.getcwd()
        log.info(f"cwd is: {self.__path}")
        self.display_count: int = 0
        self.max_displays = max_displays
        self.input_count: int = 0
        self.size = screen_size
        self.displays: List[Connection] = []
        self.inputs: List[Connection] = []

    def create_UI(self, program: int):
        """
            Starts a new instance of cmd and runs either Display.py, 0, 
            or InputScreen.py, 1
        """
        programs = ['Display.py', 'InputScreen.py']
        os.system(f"start {programs[program]}")

    def connect_display(self, port: int):
        """
            Connects Display to GameEngine
        """
        address = ("localhost", port)
        authkey = b'I hope this works'
        self.displays.append(Client(address))
        self.display_count += 1

    def connect_input(self, port: int):
        """
            Connects InputScreen to GameEngine
        """
        address = ("localhost", port)
        authkey = b'I hope this works'
        self.inputs.append(Client(address))
        self.input_count += 1

    def start_engine(self):
        """
            Starts the GameEngine object using the multiprocessing 
            library. Each Display and InputScreen is a separate 
            process that communicates with the GameEngine.
        """
        self.create_UI(0)
        log.info("Created Display")
        self.connect_display(1000)
        self.displays[0].send(self.size)
        self.create_UI(1)
        log.info("Created InputScreen")
        self.connect_input(2000)
        self.inputs[0].send('Test Input')
        log.info(self.inputs[0].recv())
        log.info(self.displays[0].recv())

    def UPDATE(self, instruction: DisplayInstruction):
        for id in range(len(self.displays)):
            if instruction.to == id:
                self.displays[id].send(instruction)

    def UPDATE_ALL(self, instruction: DisplayInstruction):
        for display in self.displays:
            display.send(instruction)

    def check_inbox(self):
        for conn in self.inputs:
            try:
                data = conn.recv()
                log.info(type(data))
                if isinstance(data, DataRequest):
                    self.displays[data.to].send(data)
                if isinstance(data, DisplayInstruction):
                    self.UPDATE(data)
            except Exception as e:
                log.info(e)
                return
        
        for conn in self.displays:
            try:
                data = conn.recv()
                if isinstance(data, DataRequest):
                    self.inputs[data.give].send(data)
            except Exception as e:
                log.info(e)
                return

    def pass_instruction(self):
        pass

def game_loop(game: GameInstance):
    game.check_inbox()
    game.UPDATE_ALL(DisplayInstruction('updateDisplay'))
    time.sleep(2)

if __name__ == '__main__':
    #set_start_method('forkserver', force = True)
    game = GameInstance((40, 40))
    game.start_engine()
    game.check_inbox()
    while 1:
        game_loop(game)
