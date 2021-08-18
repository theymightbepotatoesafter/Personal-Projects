"""
Display Screen v0.1

Author  : Christian Carter
Date    : 23 May 2021

Displays the currently selected screen onto the command line. 
Contains classes that define what a screen is and how it should be displayed.
"""
version_info = "v0.1"
import os
import enum
import logging
from copy import deepcopy
from typing import Any, List, Dict, Callable, Tuple

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

class Cell(object):

    def __init__(self, x_pos: int, y_pos: int, value: str = ' ', offset: Tuple[int, int] = (0,0)):
        self.value: str = str(value)
        self.x = x_pos
        self.y = y_pos
        self.x_off = offset[0]
        self.y_off = offset[1] 

    def __str__(self) -> str:
        return str(self.value)

    def __eq__(self, other: 'Cell') -> bool:
        if ((self.x + self.x_off) == other.x) and ((self.y + self.y_off) == other.y):
            return True
        return False

    def __add__(self, other: 'Cell') -> 'Cell':
        self.write(other.value)
    
    def write(self, new_val: str):
        self.value = new_val

class cmdDisplay(object):

    def __init__(self, size: Tuple[int, int], **kwargs):
        assert (size[0] > 15) & (size[1] > 0), "Display has to have at least ten cells"
        if len(kwargs) > 0:
            assert len(kwargs) == 1, 'buffer_size takes one argument, an int'
        self.width = size[0]
        self.height = size[1]
        self.cur_frame: cmdDisplay.Frame = self.Frame(self.height, self.width)
        self.frameBuffer: cmdDisplay.FrameBuffer = self.FrameBuffer(self, kwargs['buffer_size'])

    def Display(self):
        """Displays first valid frame in frame buffer"""
        buffer_str = self.frameBuffer.getFrame()
        print(buffer_str)

    class Frame(object):
        
        def __init__(self, height: int, width: int, generate = True):
            self.cells: List[List[Cell]] = []
            self.width = width
            self.height = height
            if generate:
                for row in range(self.height):
                    cell_list = []
                    for col in range(self.width):
                        new_cell = Cell(col, row)
                        cell_list.append(new_cell)
                    self.cells.append(cell_list)
                self.blank = deepcopy(self.cells)
            self.total_cells: int = self.height * self.width

        def __str__(self) -> str:
            # text wraping should be enabled so the str 
            # only needs to be one line
            display_str = ''
            for row in range(self.height):
                for col in range(self.width):
                    cell_val = self.cells[row][col].value
                    display_str += cell_val
            return display_str
        
        def __repr__(self):
            return f'Frame[{(self.__str__[::8])[:8]}...]'

        def fill(self, fill_char: str):
            assert len(fill_char) == 1, 'fill only uses one character'    
            for row in self.cells:
                for cell in row:
                    cell.write(fill_char)
                    
    class FrameBuffer(object):

        def __init__(self, display: 'cmdDisplay', buffer_size: int = 5):
            self.buffer: List[Tuple[cmdDisplay.Frame, bool]] = [(display.cur_frame, False)] * buffer_size
            self.cur_frame: cmdDisplay.Frame = display.cur_frame
            #self.buffer[0] = (self.cur_frame, False)
            self.display = display

        def putFrame(self, new_frame: 'cmdDisplay.Frame'):
            for frame in range(len(self.buffer)):
                if self.buffer[frame][1]:
                    continue
                self.buffer[frame] = (new_frame, True)
                return

        def putFrames(self, new_frames: List['cmdDisplay.Frame']):
            for frame in new_frames:
                self.putFrame(frame)
            return

        def stepBuffer(self):
            try:
                for tup in range(len(self.buffer)):
                    self.buffer[tup] = self.buffer[tup + 1]
            except IndexError:
                self.buffer[-1] = (self.cur_frame, False)
            return
        
        def getFrame(self):
            """Fetches the first valid frame in the frame buffer"""
            for frame in self.buffer:
                if frame[1]:
                    return frame[0]
            return self.cur_frame

class Screen(cmdDisplay):

    def __init__(self, size: Tuple[int, int], fill_char: str = ' ', **kwargs):
        super().__init__(size, **kwargs)
        self.fill = fill_char
        self.is_displaying = True
    
    def Display(self):
        if self.is_displaying:
            #os.system(f'start python')
            os.system(f'mode con: cols={self.width} lines={self.height}')
        else:
            os.system(f'start cmd && mode con: cols={self.width} lines={self.height}')
            self.is_displaying = True
        super().Display()

class Draw:
    """Contains classes for drawing objects onto the screen"""
    class Shape(cmdDisplay.Frame):

        def __init__(self, **kwargs):
            try:
                super().__init__(kwargs['height'], kwargs['width'], kwargs['generate'])
            except Exception:
                super().__init__(kwargs['height'], kwargs['width'])

        def put(self, frame: cmdDisplay.Frame):
            raise NotImplementedError('put should be implimented in the subclasses')
                 