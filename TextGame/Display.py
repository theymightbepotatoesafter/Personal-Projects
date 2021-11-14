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

class FrameBeingDrawn(DisplayError):
    def __init__(self, frame: 'Frame'):
        self.frame = frame
    def __str__(self):
        return f'Frame is in use. Please call Draw.{self.frame}.stop() before proceeding'

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
    def __init__(self, size: Tuple[int, int], draw: bool = False):
        self.h, self.w = size
        self.cells: List[List[Cell]] = []
        self.string: str = ''
        for rows in range(self.h):
            row = []
            for col in range(self.w):
                row.append(Cell())
            self.cells.append(row)
        self.draw = draw

    def __add__(self, other):
        assert self.draw == False, f'Frame is being drawn'
        assert isinstance(other, Sprite), 'Addition must be Frame + Sprite'
        for row in range(other.y, other.y + other.h):
            for col in range(other.x, other.x + other.w):
                self.cells[row][col] = other.cells[row % other.y][col % other.x]

    def __str__(self) -> str:
        assert self.draw == False, f'Frame is being drawn'
        for row in range(self.h):
            for cell in range(self.w):
                self.string += str(self.cells[row][cell])
        return self.string

class Draw:
    """ Methods for drawing frames easier """
    def __init__(self, parent: 'Frame'):
        self.self = parent
        self.self.draw = True

    def put_sprite(self, sprite: 'Sprite', position: Tuple[int, int]):
        assert self.self.draw == True, f'Frame is not drawable'
        self.self + sprite

    def fill(self, fill_char: str):
        assert self.self.draw == True, f'Frame is not drawable'
        for row in range(self.self.h):
            for col in range(self.self.w):
                self.self.cells[row][col].set_value(fill_char)

    def stop_drawing(self):
        self.self.draw = False 

class Sprite(Frame):
    """ Collection of characters forming a larger unit """
    def __init__(self, size: Tuple[int, int], chars: str, pos: Tuple[int, int], name = 'Sprite'):
        super().__init__(size)
        self.name = name
        self.string = chars
        self.x, self.y = pos
        chars = list(chars)
        for row in range(self.h):
            for col in range(self.w):
                try:
                    new_value = chars.pop(0)
                    self.cells[row][col].set_value(new_value)
                except IndexError as e:
                    log.debug((e, 'Sprite init'))
                    self.cells[row][col].set_value(new_value)

class Scene(Frame):

    def __init__(self, size: Tuple[int, int], sprites: List[Sprite], name = "Scene"):
        super().__init__(size)
        self.view = False
        self.name = name
        try:
            self.sprites = sprites
            for sprite in sprites:
                self.put_sprite(sprite)
        except IndexError:
            self.sprites = []
            log.debug('No input sprites')

    def __repr__(self):
        return f'Scene.{self.name}'

    def put_sprite(self, sprite: Sprite):
        self + sprite

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

    def print_from_instruction(self, word_list: List[str]):
        string = ''
        for word in word_list:
            string += f'{word} '
        string.strip()
        #self.clear()
        print(string)

def hide_logs():
    log.setLevel(logging.CRITICAL)

if __name__ == '__main__':
    from StationKeeper import *
    try:
        hide_logs()
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
        'print': display.print_from_instruction,
        'clear': display.clear,
        'hideLogs': hide_logs
        }
        
        def instruction_handle(instruction: Instruction):
            task = instruction.get_task()
            args = instruction.get_args()
            if task in TASK:
                if args != None:
                    try:
                        TASK[task](*args)
                        return
                    except Exception as e:
                        log.debug((e, 'instruction handle'))
                TASK[task]()

        log.setLevel(logging.DEBUG)
        Display
        while True:
            instruction = conn.recv()
            instruction_handle(instruction)
    
    except ConnectionResetError:
        log.debug('Exiting...')
        time.sleep(2)
        os.system('exit')
