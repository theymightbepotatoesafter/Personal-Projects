"""
Game Engine v0.4

Author  : Christian Carter
Date    : 30 Sep 2021

Code for routing Intsructions and creating Frames to be displayed
"""
version_info = 'v0.4'

from Instruction import *
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
    def __init__(self, title: str, screen_size: Tuple[int, int], queue: Queue, clock_time: float, max_displays: int):
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
        self.run: c_bool = Value(c_bool, True)
        ctx = get_context()
        self.queue = Queue(20, ctx = ctx)
        self.parent_queue = queue
        log.debug('Queue started...')

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
        get = Process(target = self.instruction_loop, args = (self.queue, ))
        get.start()

    def start(self):
        self.instruction_loop()

    def stop(self):
        self.run.value = False

    def hide_logs(self):
        log.setLevel(logging.CRITICAL)
        for input in range(len(self.inputs)):
            self.instruction_put(Instruction('hideLogs', to = f'input{input}'))
        for display in range(len(self.displays)):
            self.instruction_put(Instruction('hideLogs', to = f'display{display}'))

    def instruction_loop(self, queue: Queue):
        log.debug('Instruction loop starting...')
        while self.run.value == True:
            try:
                self.input_get(queue)
                instruction = queue.get(True, self.wait)
                self.instruction_handle(instruction)
            except Empty:
                #log.debug('Queue is empty...')
                continue
        log.info('Exiting instruction loop...')

    def instruction_handle(self, instruction: Instruction):
        """ Sends instructions to and from where they need to go """
        assert isinstance(instruction, Instruction), f'Cannot handle {type(instruction)}'
        destination = instruction.destination()
        if 'input' in destination:
            num = int(destination[-1])
            self.inputs[num].send(instruction)
            log.debug(f'Sent to input {num}')
            return
        if 'displayEngine' in destination:
            task = instruction.get_task()
            if task == 'stop':
                self.stop()
                return
            if task == 'start':
                self.start()
                return
        if 'display' in destination:
            num = int(destination[-1])
            self.displays[num].send(instruction)
            log.debug(f'Sent to display {num}')
            return
        if 'game' in destination:
            self.parent_queue.put(instruction)
            log.debug(f'Sent to game')
            return
        log.debug(f'Did not recognize destination {destination}')        

    def input_get(self, queue):
        connection = wait(self.inputs, self.wait)
        #log.debug(f'Connections ready: {connection}')
        try:
            for conn in connection:
                queue.put(conn.recv())
                continue
        except IndexError:
            log.debug('No instructions received...')
        except Exception as e:
            log.debug(e)
    
    def instruction_put(self, instruction: Instruction):
        assert isinstance(instruction, Instruction), f'{instruction} is not Instruction'
        log.debug('Putting instruction in queue...')
        try:
            self.queue.put(instruction)
        except Exception as e:
            log.debug(e)
            return
        finally:
            log.debug('Instruction put!')

if __name__ == '__main__':
    log.setLevel(logging.CRITICAL)
    clock = 0.1
    ctx = get_context()
    queue = Queue(5, ctx = ctx)
    game = Instance('game', (40, 70), queue, clock, 2)
    game.default_start()
    log.debug('Instance started...')
    new_instruction = Instruction(task = 'getFromPrompt', args = ('Input: ', 'display0'), to = 'input0')
    game.instruction_put(new_instruction)
    log.debug('new instruction sent')
    while True:
        continue