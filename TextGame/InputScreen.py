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
import time
from Instruction import *
from Display import Frame
from multiprocessing.connection import Connection, Listener, wait

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

def get_input(input_message: str = 'Input: '):
    """ Get input from the command line input screen """
    data: str = None
    while data == None:
        data = input(input_message)
    return data

VALID_INSTRUCTION = ['print', 'clear', 'fill']

def check_input(data: str):
    data = data.split()
    for word in data:
        if word in VALID_INSTRUCTION:
            try:
                assert word == data[0], 'Incorrect format'
            except AssertionError:
                cls()
                check_input(get_input('Incorrect format. Please try again.\nInput: '))
            return create_instruction(data)
    cls()
    check_input(get_input('Input not recognized. Please try again\nInput: '))

def create_instruction(data: List[str]) -> Instruction:
    command = data.pop(0)
    if command == 'print':
        print_str = ''
        for word in data:
            print_str += f'{word} '
        Frame = print_to_frame(print_str.strip())
    if command == 'fill':
        Frame = fill_frame(data[0])
    if command == 'clear':
        Frame = fill_frame(' ')
    return DisplayInstruction('updateFrameBuffer', 0, Frame)

def fill_frame(data: str):
    return Frame(height, width).fill(data)

def print_to_frame(data: str) -> Frame:
    new_frame = Frame(height, width)
    chars = list(data)
    try:
        for y in range(height):
            for x in range(width):
                char = chars.pop(0)
                new_frame.cells[x][y].write(char)
    except IndexError:
        pass    
    return new_frame

def send_input(conn: Connection):
    """ Send input to the game engine """
    data = get_input()
    data = check_input(data)

    conn.send(data)
    cls()
    print("Instruction sent")

def main(conn: Connection):
    try:
        send_input(conn)
    except KeyboardInterrupt:
        quit()
    main(conn)

if __name__ == "__main__":
    address = ('localhost', 2000)
    authkey = b'I hope this works'
    listener = Listener(address)
    conn = listener.accept()
    log.info(f"Connection accepted from {listener.last_accepted}")
    queue = wait([conn])
    for connection in queue:
        log.info(conn.recv())
    conn.send('Waiting for instructions to input')
    time.sleep(2)
    conn.send(DataRequest(0, 0, 5))
    data = conn.recv()
    assert type(data) == DataRequest, 'Something got fucked up'
    height, width = DataRequest.data
    main(conn)