"""
Input screen v0.2

Author  : Christian Carter
Date    : 18 Aug 2021

Code for interpreting the input of the 
command prompt and relaying that info 
to other code to run the game.
"""
version_info = "v0.2"
import logging
import os
from multiprocessing import Queue
from Instruction import *

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

class InputEvent(Exception):
    """ Define an input flag for interupting the game engine """
    def __init__(self):
        pass

def cls():
    """ Clear the terminal screen """
    os.system('cls')

def get_input():
    """ Get input from the command line input screen """
    data = None
    while data == None:
        data = input("Input: ")
    return data

def send_input(queue: Queue):
    """ Send input to the game engine """
    data = pickle.dumps(get_input())
    queue.put(data)
    cls()

def main(queue: Queue):
    try:
        send_input(queue)
    except KeyboardInterrupt:
        quit()
    main(queue)