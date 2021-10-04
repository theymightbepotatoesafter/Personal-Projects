"""
Game Engine v0.4

Author  : Christian Carter
Date    : 30 Sep 2021

Code for routing Intsructions and creating Frames to be displayed
"""
version_info = 'v0.4'

import Instruction
import logging
from ctypes import c_bool
from multiprocessing import Value, get_context
from multiprocessing.connection import Client, Connection, wait
from multiprocessing.context import Process
from multiprocessing.queues import Queue
from queue import Empty, Full
import os
import time
from typing import List, Tuple

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

class Instance:
    """ An instance of the game engine """
    def __init__(self, title: str, screen_size: Tuple[int, int], clock_time: float, max_displays: int, max_instructions: int = 20):
        self.__path = os.getcwd()
        log.info(f'cwd is {self.__path}')
        self.max_d = max_displays
        self.wait = clock_time
        self.d_count: int = 0
        self.i_count: int = 0
        self.displays: List[Connection] = []
        self.inputs: List[Connection] = []
        self.size = screen_size
        self.title = title
        self.max_instruct = max_instructions
        self.run: c_bool = Value(c_bool, True)

    def create_UI(self, ui: str):
        """ Starts a new python interpreter running the input ui program """ 
        os.system(f'start cmd /k python {self.__path}\\{ui}')

    def connect(self, io: str, port: int, authkey: bytes = b'password'):
        """ Connects displays to the game engine """
        address = ('localhost', port)
        auth = authkey       
        if io == 'displays':
            self.displays.append(Client(address))
            self.d_count += 1
        if io == 'inputs':
            self.inputs.append(Client(address))
            self.i_count += 1

    def default_start(self):
        log.info('Default start...')
        self.create_UI('Display.py')
        self.create_UI('InputScreen.py')
        self.connect('inputs', 2000)
        log.debug('display connected...')
        self.connect('displays', 1000)
        log.debug('input connected...')
        self.displays[0].send((self.size, self.title))
        self.inputs[0].send('Connection succesfull')
        log.debug('Sent input test')
        self.instruction_loop()

    def start(self):
        self.instruction_loop()

    def stop(self):
        self.run.value = False

    def hide_logs(self):
        log.setLevel(logging.CRITICAL)

    def instruction_loop(self):
        ctx = get_context()
        queue = Queue(self.max_instruct, ctx = ctx)
        log.debug('Queue started...')
        get = Process(target = self.instruction_get, args = (queue,))
        get.start()
        while self.run.value == True:
            try:
                instruction = queue.get(True, self.wait)
                self.instruction_handle(instruction)
            except Empty:
                #log.debug('Queue is empty...')
                continue
        get.join(2.0)
        log.info('Exiting instruction loop...')

    def instruction_handle(self, instruction: Instruction):
        """ Sends instructions to and from where they need to go """
        assert isinstance(instruction, Instruction), f'Cannot handle {type(instruction)}'
        destination = instruction.destination()
        if 'input' in destination:
            num = int(destination[-1])
            log.debug(num)
            self.inputs[num].send(instruction)
            log.debug(f'Sent to input {num}')
            return
        if 'displayEngine' in destination:
            task = instruction.get_task()
            if task == 'stop':
                self.stop()
                return
        if 'display' in destination:
            num = int(destination[-1])
            log.debug(num)
            self.displays[num].send(instruction)
            log.debug(f'Sent to display {num}')
            return
        log.debug(f'Did not recognize destination {destination}')        

    def instruction_get(self, send_queue: Queue):
        while True:
            connection = wait(self.displays + self.inputs, self.wait)
            #log.debug(f'Connections ready: {connection}')
            try:
                for conn in connection:
                    send_queue.put(conn.recv())
                    continue
            except IndexError:
                log.debug('No instructions received...')
                continue
            except Exception as e:
                log.debug(e)
                continue

if __name__ == '__main__':
    clock = 0.1
    game = Instance('game', (40, 70), clock, 2)
    game.default_start()