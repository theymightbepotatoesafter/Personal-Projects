"""
Input Screen v0.4

Author  : Christian Carter
Date    : 30 Sep 20201

Code to interpret input from the command line
"""
version_info = 'v0.4'

from ctypes import c_bool
from queue import Empty, Full
from multiprocessing import Process, Value, get_context
from multiprocessing.connection import Connection, Listener, wait
from multiprocessing.queues import Queue
from Instruction import *
import logging
import os
import time
from typing import Dict, List

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

busy: c_bool = Value(c_bool, False)
run: c_bool = Value(c_bool, True)

class InputInterupt(Exception):
    def __init__(self):
        log.info('Input Interupt')

    def __str__(self):
        return 'Input Interupt'

VALID_INSTRUCTION = ['print', 'clear', 'fill', 'stop']

def cls():
    """ Clears the terminal """
    os.system('cls')

def get_input(message: str):
    """ Get input from the terminal """
    log.debug('Getting input...')
    return input(message)

def check_input(input: str, instruction_set = VALID_INSTRUCTION, message: str = 'Input: '):
    log.debug('Checking input...')
    input = input.split()
    if input[0] == 'help':
        return check_input(get_input(help(message)), instruction_set)
    for word in input:
        if word in instruction_set:
            if word == input[0]:
                log.debug('Valid command!')
                return input
            return check_input(get_input(f'Incorrect format, please try again\n{message}'), instruction_set, message)
    return check_input(get_input(f'Input not recognized, recognized inputs are {str(instruction_set)} please try again.\n{message}'),
            instruction_set, message)

def create_instruction(input: List[str], to: str) -> Instruction:
    task = input.pop(0)
    for argument_num in range(len(input)):
        try:
            input[argument_num] = int(input[argument_num])
        except Exception as e:
            log.debug(e)
    args = tuple(input)
    log.debug('Instruction created...')
    log.debug(args)
    if task == 'stop':
        return Instruction(task)
    return Instruction(task, args, to)


def instruction_get(send_queue: Queue, connection: List[Connection], busy_bool: c_bool, run_bool: c_bool):
    queue: List[Instruction] = []
    while True:
        busy = busy_bool.value
        log.debug('Getting instructions...')
        log.debug(busy)
        conn = wait(connection, 0.5)
        try:
            log.debug('trying...')
            try:
                instruction: Instruction = conn[0].recv()
                log.debug(conn)
            except ConnectionResetError:
                log.debug('Exiting...')
                os.system('exit')
                run_bool.value = False
                quit()
            except Exception as e:
                log.debug(e)
            log.debug(instruction)
            log.debug(busy)
            log.debug('testing if busy true')
            if busy == True:
                queue.append(instruction)
                log.debug('Instruction queue appended')
                continue
            log.debug('testing if busy false')
            if busy == False:
                log.debug('busy is false')
                try:
                    log.debug('Trying to put instruction on queue...')
                    if len(queue) > 0:
                        log.debug('Grabbing instruction from local queue')
                        queue.append(instruction)
                        log.debug('Instruction queue appended...')
                        send_queue.put(queue.pop(0), timeout = 0.1)
                        log.debug('Instruction sent...')
                        continue
                    send_queue.put(instruction, timeout = 0.1)
                    log.debug(f'Put instruction on queue\n{send_queue}')
                    continue
                except Full:
                    log.debug('Queue is full!')
                    continue
                except UnboundLocalError as e:
                    log.debug(e)
                    continue
                except Exception as e:
                    log.debug(e)
                    continue
            log.debug('Didn\'t perform any tasks')
        except IndexError:
            log.debug('index error')
            continue
        except Exception as e:
            log.debug((e, 'instruction_get'))
            continue

def change_title(new_title: str):
    os.system(f'title {new_title}')

def hide_logs():
    log.setLevel(logging.CRITICAL)
   
if __name__ == '__main__':
    address = ('localhost', 2000)
    auth = b'password'
    with Listener(address) as listener:
        conn = listener.accept()
        log.debug(f'Connection accepted from {listener.last_accepted}...')
        tasks = conn.recv()
        
    def send_input(message: str = 'Input: ', to = 'displayEngine', instruction_set: List = tasks):
        busy.value = True
        instruction = get_input(message)
        instruction = check_input(instruction, instruction_set, message)
        instruction = create_instruction(instruction, to)
        log.debug('Input retrieved!')
        conn.send(instruction)
        log.debug('Input sent!')
        busy.value = False
    
    TASK = {}
    TASK['getFromPrompt']= send_input
    TASK['changeTitle'] = change_title
    TASK['hideLogs'] = hide_logs
    
    def help(input_message: str):
        help_message = 'Here are the commands that you can currently use\n\n'
        for key in tasks:
            help_message += f'{key}\n'
        help_message += f'{input_message}'
        return help_message
    
    def instruction_handle(instruction: Instruction):
        """ Separate procees to handle instructions """
        assert isinstance(instruction, Instruction), f'Cannot handle {type(instruction)}!'
        log.debug('Handling instruction...')
        task = instruction.get_task()
        args = instruction.get_args()
        try:
            log.debug(task)
            log.debug(args)
            log.debug('Trying...')
            if task in TASK:
                log.debug('Task is in Task')
                if args == None:
                    TASK[task]()
                    log.debug('Task with no args handled')
                    return
                TASK[task](*args)
                log.debug('Task handled')
                return
            log.debug('Task wasn\'t handled')
        except Exception as e:
            log.debug(e)

    ctx = get_context()         
    instruction_queue = Queue(5, ctx = ctx)
    log.setLevel(logging.DEBUG)
    get = Process(target = instruction_get, args = (instruction_queue, [conn], busy, run))
    get.start()

    while run.value == True:
        #log.debug(run.value)
        try:
            instruction = instruction_queue.get(True, 0.5)
            log.debug(f'Instruction {instruction} got...')
            instruction_handle(instruction)
        except Empty:
            #log.debug('Queue is empty!')
            #send_input()
            continue
    os.system('exit')
