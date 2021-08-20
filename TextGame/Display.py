"""
Display Screen v0.2

Author  : Christian Carter
Date    : 10 June 2021

Displays the currently selected screen onto the command line. 
Contains classes that define what a screen is and how it should be displayed.
"""
version_info = "v0.2"
import os
import pickle
from typing import Set, List, Tuple
from operator import attrgetter
from queue import Empty
from multiprocessing import Queue
import logging

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

class DisplayError(Exception):
    def __init__(self):
        raise NotImplementedError("Base class, should not be called")

class NoBufferSpace(DisplayError):
    def __init__(self, buffer: 'FrameBuffer'):
        self.buffer = buffer
    def __str__(self):
        return f"No space in FrameBuffer {self.buffer}"

class Cell(object):
    
    def __init__(self, x_pos: int, y_pos: int, value: str = ''):
        """A cell on the screen. Contains row, column, and value information"""
        self.x = x_pos
        self.y = y_pos
        self.value = value

    def write(self, value: str):
        """Writes a value to the cell"""
        self.value = value

class Frame(object):
            
    def __init__(self, height: int, width: int, 
                 priority: int = 1, pos_LHC: Tuple[int, int] = (0,0)):
        """
            A Frame object consists of a matrix of cells and a start position.
            The start position determines where the left-hand corner of the Frame
            object will be
        """
        self.priority = priority
        self.cells: List[List[Cell]] = []
        self.height = height
        self.width = width
        self.pos = pos_LHC
        self.row_start = pos_LHC[0]
        self.col_start = pos_LHC[1]
        for row in range(height):
            col_list = []
            for col in range(width):
                new_cell = Cell(col, row)
                col_list.append(new_cell)
            self.cells.append(col_list)
    
    def __lt__(self, other: 'Frame') -> bool:
        return self.priority < other.priority

    def __add__(self, other: 'Frame') -> 'Frame':
        """
            adds two Frame objects together based on their priorities
            and returns the altered Frame object
        """        
        intersect_bool, (row_index, col_index) = self.intersect(self, other)
        assert intersect_bool, 'Frame objects do not intersect'
        
        if other.priority >= self.priority:
            priority = other
            secondary = self
        else:
            priority = self
            secondary = other
        
        for row in range(len(row_index)):
            for col in range(len(col_index)):
                prio_row = row_index[row] - priority.row_start
                prio_col = col_index[col] - priority.col_start
                sec_row = row_index[row] - secondary.row_start
                sec_col = col_index[col] - secondary.col_start
                secondary.cells[sec_row][sec_col].write(
                            priority.cells[prio_row][prio_col].value)
        return secondary

    def __str__(self) -> str:
        return_str = ""
        for row in self.cells:
            for cell in row:
                return_str += cell.value
        return return_str

    def intersect(self, other: 'Frame') -> Tuple[bool, Tuple[Set, Set]]:
        """returns whether the two Frame objects intersect"""
        self_row_index = set([y for y in range(
            self.row_start, self.row_start + self.height)])
        self_col_index = set([x for x in range(
            self.col_start, self.col_start + self.width)])
        other_row_index = set([y for y in range(
            other.row_start, other.row_start + other.height)])
        other_col_index = set([x for x in range(
            other.col_start, other.col_start + other.width)])
        log.debug(f"""self row indexes: {self_row_index}\n
                      self col indexes: {self_col_index}""".strip())
        log.debug(f"""other row indexes: {other_row_index}\n
                      other col indexes: {other_col_index}""".strip())
        set_1 = self_row_index.intersection(other_row_index)
        set_2 = self_col_index.intersection(other_col_index)
        sets = set_1, set_2
        if (len(set_1) > 0 and len(set_2) > 0):
            return True, sets
        return False, sets

    def size(self) -> Tuple[int, int]:
        """returns a tuple of height and width"""
        return (self.height, self.width)

    def fill(self, fill_char: str):
        """fills the Frame object with the fill character"""
        for row in self.cells:
            for cell in row:
                cell.write(fill_char)

class FrameBuffer(object):
    
    def __init__(self, buffer_len: int, display: 'cmdDisplay', 
                frames: List[Frame] = [], max_frames: int = 10, **kwargs):
        """
            The FrameBuffer is an object that holds, writes, 
            and reads Frame objects.
        
            Holding:
                FrameBuffer always holds the current Frame 
                object but may contain: 
                    empty Frame objects,
                    the next Frame object,
                    previous Frame objects,
                    future Frame objects
        
            Writing:
                FrameBuffer.put_frame(new_frame: Frame = '') 
                puts input frame in first available slot

            Reading:
                FrameBuffer.get_frame() returns the current frame, 
                depends on self.frame_index.Increment self.frame_index 
                with FrameBuffer.next()

         ############################################################################
         #                                                                          #
         # Every Display object must have a FrameBuffer object in order to function #
         #                                                                          #
         ############################################################################
        """
        self.max_frames = max_frames
        self.parent = display
        self.buffer_state = False # sets whether or not the frame buffer exists
        self.buffer = self.generate_buffer(buffer_len, self.parent, frames)
        log.debug(self.buffer)
        self.display_index = 0 # Beginning index for fetching Frame objects
        assert_err_txt = f"""
        Buffer lengths are different by {buffer_len - len(self.buffer)}!
        buffer_len: {buffer_len} len(self.buffer): {len(self.buffer)}""".strip()
        assert buffer_len == len(self.buffer), assert_err_txt # making sure buffer created right
        self.len = buffer_len

    def generate_buffer(self, buffer_len: int, display: 'cmdDisplay', frames: List[Frame]):
        """
            If the frame buffer is not pre-filled this function will be
            called and will generate the frame buffer to the specified length
        """
        if self.buffer_state == True:
            return
        log.debug("running generate_buffer")
        buffer_list = []
        height, width = display.size()
        
        assert len(frames) <= buffer_len, 'Too many initializing Frame objects'
        
        for frame in frames:
            buffer_list.append((frame, True))
        while len(buffer_list) < buffer_len:
            new_frame = Frame(height, width)
            buffer_list.append((new_frame, False))
        
        self.buffer = buffer_list
        self.buffer_state = True
        return
    
    def is_full(self) -> bool:
        """ Returns whether or not the FrameBuffer is full """
        for frame in self.buffer:
            if not frame[1]:
                return False
        return True

    def put_frame(self, new_frame: Frame):
        """ Put a frame in the first open slot of the FrameBuffer object """
        if self.is_full():
            raise NoBufferSpace(self)

        for i in range(self.len):
            test_frame = self.buffer[(self.display_index + i) % self.len]
            if not test_frame[1]:
                test_frame[0] = new_frame
                test_frame[1] = True
                return
                    
    def get_frame(self) -> Frame:
        """ Return the frame from the current frame index """
        return self.buffer[self.display_index][0]

    def next(self):
        """ Shift the frame buffer by one """
        # sets current frame to empty/invalid
        self.buffer[self.display_index][1] = False
        # increments display_index 
        self.display_index = (self.display_index + 1) % self.len 
        
class cmdDisplay(object):

    def __init__(self, height: int, width: int, queue: Queue,
                    buffer_len: int = 5, fill_char: str = ' ', **kwargs):
        """
            cmdDisplay sets the size and displays Frames that are held
            in the FrameBuffer.
        """
        self.height = height
        self.width = width
        self.queue = queue
        self.master_frame = Frame(height, width)
        self.frame_buffer = FrameBuffer(buffer_len, self)
        self.fill_char = fill_char
        self.kwargs = kwargs
        
    def name(self) -> int:
        try:
            return self.kwargs['name']
        except KeyError:
            return 0

    def apply(self):
        os.system(f"mode con: cols={self.width} lines={self.height}")

    def size(self) -> Tuple[int, int]:
        return (self.height, self.width)

    def update_frame_buffer(self):
        try:
            data = pickle.loads(self.queue.get(True, .1))
            assert type(data) == Frame, "Data needs to be a Frame object"
            try:
                self.frame_buffer.put_frame(data)
                self.update_frame_buffer()
            except NoBufferSpace:
                return
        except Empty:
            log.debug("No data available in time frame")

    def update_display(self):
        cur_frame = self.frame_buffer.get_frame()
        self.frame_buffer.next()
        self.update_frame_buffer()
        print(str(cur_frame))

def buildCompFrame(frame: List[Frame]) -> Frame:
    """
        builds Frame object composed of the sum of the Frame objects
        in the list: frame. Frame objects must be the same size
    """
    master_frame = Frame(frame[0].size()[0], frame[0].size()[1], 0)
    for f in sorted(frame, key = attrgetter('priority')):
        master_frame = master_frame + f
    return master_frame
