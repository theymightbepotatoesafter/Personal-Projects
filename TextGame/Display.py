"""
Display Screen v0.4

Author  : Christian Carter
Date    : 30 Sep, 2021

Displays Frames to the Command Line
"""
version_info = 'v0.4'

import logging
from multiprocessing.connection import Listener
import os
import time
from typing import List, Tuple
from Instruction import *

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

class DisplayError(Exception):
    def __init__(self):
        raise NotImplementedError("Base class. Should not be called!")

class InstructionNotExecuted(DisplayError):
    def __init__(self, display_name):
        log.critical(f'Instruction did not execute on {self.disp}!')
        self.disp = display_name

    def __str__(self):
        return f'Instruction did not execute on {self.disp}!'

class NoBufferSpace(DisplayError):
    def __init__(self, display_name):
        log.debug(f'No buffer space in buffer {display_name}')
        self.disp = display_name

    def __str__(self):
        return f'No buffer space in buffer {self.disp}'

class Cell:
    """ Smallest unit of the display. Holds one character """
    def __init__(self, value: str = ' '):
        self.value = value

    def __str__(self) -> str:
        return self.value

    def set_value(self, value: str):
        self.value = value

class Frame(object):
    """ Frames hold cells and are displayed with the display """
    def __init__(self, size: Tuple[int, int], draw: bool = True):
        self.h, self.w = size
        self.cells: List[List[Cell]] = []
        self.string: str = ''
        for rows in range(self.h):
            row = []
            for col in range(self.w):
                row.append(Cell())
            self.cells.append(row)
        if draw:
            self.Draw = self.Draw(self)

    def __add__(self, other):
        assert isinstance(other, Sprite), 'Addition must be Frame + Sprite'
        for row in range(other.y, other.y + other.h):
            for col in range(other.x, other.x + other.w):
                self.cells[row][col] = other.cells[row % other.y][col % other.x]

    def __str__(self) -> str:
        if len(self.string) < (self.h * self.w):
            self.make_str()
        return self.string
        
    def make_str(self):
        for row in range(self.h):
            for cell in range(self.w):
                self.string += str(self.cells[row][cell])

    class Draw:
        """ Methods for drawing frames easier """
        def __init__(self, parent: 'Frame'):
            self.self = parent

        def put_sprite(self, sprite: 'Sprite', position: Tuple[int, int]):
            sprite.place(self.self, position)

        def fill(self, fill_char: str):
            for row in range(self.self.h):
                for col in range(self.self.w):
                    self.self.cells[row][col].set_value(fill_char)

class Sprite(Frame):
    """ Collection of characters forming a larger unit """
    def __init__(self, size: Tuple[int, int], chars: str, draw: bool = False):
        super().__init__(size, draw)
        for row in range(self.h):
            for col in range(self.w):
                self.cells[row][col].set_value(chars.pop(0))

    def place(self, frame: Frame, position: Tuple[int, int]) -> Frame:
        self.x, self.y = position
        frame + self

class FrameBuffer(object):
    """ Holds frames for the display """
    def __init__(self, max_length: int):
        self.max = max_length
        self.buffer: List[Frame] = []
        log.debug('Buffer created')

    def is_full(self) -> bool:
        """ Returns if buffer is full """
        if len(self.buffer) >= self.max:
            return True
        return False

    def len(self):
        return len(self.buffer)

    def put(self, Frame: Frame):
        self.buffer.append(Frame)

    def get(self) -> Frame:
        return self.buffer.pop(0)

    def clear(self):
        self.buffer: List[Frame] = []
    
class Display:
    """ Display and display handling methods """
    def __init__(self, size: Tuple[int, int], title: str = 'Display.py'):
        self.h, self.w = size
        self.s = size
        self.blank: Frame = Frame(size, False)
        self.buffer: FrameBuffer = FrameBuffer(5)
        self.buffer.put(self.blank)
        self.name = self
        self.apply_size()
        self.apply_title(title)

    def apply_size(self):
        os.system(f'MODE CON: COLS={str(self.w)} LINES={str(self.h)}')

    def apply_title(self, title: str):
        os.system(f'title {title}')
    
    def size(self) -> Tuple[int, int]:
        return self.s

    def resize(self, size: Tuple[int, int]):
        self.h, self.w = size
        self.apply_size()

    def update(self):
        try:
            assert self.buffer.len() > 0, 'No Frames in FrameBuffer!'
        except AssertionError as e:
            log.debug(e)
            self.buffer.put(self.blank)
        print(str(self.buffer.get()))

    def clear(self):
        os.system('cls')

    def print(self, word_list: List[str]):
        string = ''
        for word in word_list:
            string += f'{word} '
        string.strip()
        #self.clear()
        print(string)

if __name__ == '__main__':
    try:
        address = ('localhost', 1000)
        auth = b'password'
        with Listener(address) as listener:
            conn = listener.accept()
            log.info(f'Connection accepted from {listener.last_accepted}')
        size, title = conn.recv()
        display = Display(size, title)

        TASK = {
        'putFrame': display.buffer.put,
        'update': display.update,
        'resize': display.resize,
        'clearBuffer': display.buffer.clear,
        'print': display.print,
        'clear': display.clear
        }
        
        def instruction_handle(instruction: Instruction):
            task = instruction.get_task()
            args = instruction.get_args()
            if task in TASK:
                try:
                    TASK[task]()
                except Exception as e:
                    TASK[task](args)
                    log.debug(e)

        while True:
            log.setLevel(logging.INFO)
            instruction = conn.recv()
            instruction_handle(instruction)
    
    except ConnectionResetError:
        log.debug('Exiting...')
        time.sleep(2)
        os.system('exit')
        