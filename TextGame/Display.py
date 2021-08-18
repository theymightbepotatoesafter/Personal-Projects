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
from multiprocessing.connection import Connection, Client
import argparse
import logging


logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

class DisplayError(Exception):
    def __init__(self):
        pass

class NoBufferSpace(DisplayError):
    def __init__(self, frame_buff: 'FrameBuffer', message: str):
            self.name = frame_buff
            self.message = message

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
        self.buffer = self.generate_buffer(buffer_len, self.parent, frames)
        log.debug(self.buffer)
        self.display_index = 0
        assert_err_txt = f"""Buffer lengths are different by 
        {buffer_len - len(self.buffer)}!\nbuffer_len: {buffer_len} 
        len(self.buffer): {len(self.buffer)}""".strip()
        assert buffer_len == len(self.buffer), assert_err_txt
        self.len = buffer_len

    def generate_buffer(self, buffer_len: int, display: 'cmdDisplay', 
                        frames: List[Frame]) -> List[Tuple[Frame, bool]]:
        """
            If the frame buffer is not pre-filled this function will be
            called and will generate the frame buffer to the specified length
        """
        log.debug("running generate_buffer")
        buffer_list = []
        height, width = display.size()
        assert len(frames) <= buffer_len, 'Too many initializing Frame objects'
        init_frames = frames
        for frame in init_frames:
            buffer_list.append((frame, True))
        while len(buffer_list) < buffer_len:
            new_frame = Frame(height, width)
            buffer_list.append((new_frame, False))
        return buffer_list

    def put_frame(self, new_frame: Frame):
        """ Put a frame in the first open slot of the FrameBuffer object """
        assert len(self.buffer) == self.len, 'Buffer lengths are different!'
        for i in range(self.len):
            test_frame = self.buffer[(self.display_index + i) % self.len]
            if not test_frame[1]:
                test_frame[0] = new_frame
                test_frame[1] = True
                return
        raise NoBufferSpace(self, 
        f"FrameBuffer:{self} on cmdDisplay:{self.parent} has run out of space")
                    
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

    def __init__(self, height: int, width: int, 
                    buffer_len: int, fill_char: str = ' ', **kwargs):
        self.height = height
        self.width = width
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

    def display(self):
        cur_frame = self.frame_buffer.get_frame()
        self.frame_buffer.next()
        print(str(cur_frame))

def cli() -> object:
    """ Get arguments from command line """
    
    log.info("starting parser")
    parser = argparse.ArgumentParser(description = "Linkage argument parser")
    parser.add_argument("--name", type = str, required = True, 
                        help = "address name")
    parser.add_argument("--num", type = int, required = True, 
                        help = "address int")
    parser.add_argument("--auth", type = str, required = True, 
                        help = "auth key")
    args = parser.parse_args()
    log.info(f"args got {args}")
    return args

def buildCompFrame(frame: List[Frame]) -> Frame:
    """
        builds Frame object composed of the sum of the Frame objects
        in the list: frame. Frame objects must be the same size
    """
    master_frame = Frame(frame[0].size()[0], frame[0].size()[1], 0)
    for f in sorted(frame, key = attrgetter('priority')):
        master_frame = master_frame + f
    return master_frame

if __name__ == "__main__":
    try:
        args = cli()
    except Exception:
        args = {"name": "localhost", "num": 2001}
    client = Client((args.name, args.num))
    info_present = client.poll()
    while info_present == False:
        info_present = client.poll()
        log.info("no info present")
    data: Tuple[Tuple[int, int], int] = pickle.loads(client.recv())
    display = cmdDisplay(data[0][0], data[0][1], 10, name = data[1])
    assert display.size() == data[0], f"""display_{display.name()} 
    is not the correct size"""
    display.apply()

