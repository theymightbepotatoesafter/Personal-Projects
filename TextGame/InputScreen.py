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

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

def cls():
    """ Clear the terminal screen """
    os.system('cls')

class Instruction(object):

    def __init__(self):
        raise NotImplementedError("Not implimented yet")

