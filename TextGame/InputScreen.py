"""
Input Screen v0.4

Author  : Christian Carter
Date    : 30 Sep 20201

Code to interpret input from the command line
"""
version_info = 'v0.4'

from ctypes import c_bool
from queue import Empty, Full
from multiprocessing import Process, Value, get_context, ProcessError
from multiprocessing.connection import Connection, Listener, wait
from multiprocessing.queues import Queue
from Instruction import *
import logging
import os
import time
from typing import List

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

busy: c_bool = Value(c_bool, False)
run: c_bool = Value(c_bool, True)

class InputInterupt(Exception):
    def __init__(self):
        log.info('Input Interupt')

    def __str__(self):
        return 'Input Interupt'

def cls():
    """ Clears the terminal """
    os.system('cls')

def get_input(message: str):
    """ Get input from the terminal """
    log.debug('Getting input...')
    return input(message)

VALID_INSTRUCTION = ['print', 'clear', 'fill', 'stop']

def check_input(input: str):
    log.debug('Checking input...')
    input = input.split()
    for word in input:
        if word in VALID_INSTRUCTION:
            if word == input[0]:
                log.debug('Valid command!')
                return create_instruction(input)
            return check_input(get_input('Incorrect format, please try again\nInput: '))
    return check_input(get_input('Input not recognized, please try again.\nInput: '))

def create_instruction(input: List[str]) -> Instruction:
    task = input.pop(0)
    log.debug('Instruction created...')
    if task == 'stop':
        return Instruction(task)
    return Instruction(task, input, 'display0')

def send_input(message: str = 'Input: '):
    busy.value = True
    instruction = get_input(message)
    instruction = check_input(instruction)
    log.debug('Input retrieved!')
    conn.send(instruction)
    log.debug('Input sent!')
    busy.value = False

def instruction_get(send_queue: Queue, connection: List[Connection], busy_bool: c_bool, run_bool: c_bool):
    queue: List[Instruction] = []
    while True:
        busy = busy_bool.value
        conn = wait(connection, 0.1)
        if len(conn) > 0:
            try:
                instruction = conn[0].recv()
            except ConnectionResetError:
                log.debug('Exiting...')
                time.sleep(2)
                os.system('exit')
                run_bool.value = False
                quit()
            log.debug(instruction)
            if busy == True:
                queue.append(instruction)
                log.debug('Instruction queue appended')
                continue
        if busy == False:
            try:
                if len(queue) > 0:
                    queue.append(instruction)
                    log.debug('Instruction queue appended')
                    send_queue.put(queue.pop(0), timeout = 0.1)
                    log.debug('Instruction sent...')
                    continue
                send_queue.put(instruction, timeout = 0.1)
            except Full:
                log.debug('Queue is full!')
                continue
            except UnboundLocalError:
                continue

if __name__ == '__main__':
    address = ('localhost', 2000)
    auth = b'password'
    with Listener(address) as listener:
        conn = listener.accept()
        log.info(f'Connection accepted from {listener.last_accepted}...')
        log.info(conn.recv())

    TASK = {
        'getFromPrompt': send_input
    }

    def instruction_handle(instruction: Instruction):
        """ Separate procees to handle instructions """
        assert isinstance(instruction, Instruction), f'Cannot handle {type(instruction)}!'
        task = instruction.get_task()
        args = instruction.get_args()
        if task in TASK:
            if args == None:
                TASK[task]()
                return
            TASK[task](args)
            return

    ctx = get_context()         
    instruction_queue = Queue(ctx = ctx)
    log.setLevel(logging.INFO)
    get = Process(target = instruction_get, args = (instruction_queue, [conn], busy, run))
    get.start()

    while run.value == True:
        log.debug(run.value)
        try:
            instruction = instruction_queue.get(True, 0.5)
            instruction_handle(instruction)
        except Empty:
            log.debug('Queue is empty!')
            #send_input()
            continue
    os.system('exit')

