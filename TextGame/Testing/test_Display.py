import unittest
from Display import *
from time import sleep
from os import system

class TestFrame(unittest.TestCase):

    baseFrame = Frame(50, 50, 0)

    def test_init(self):
        self.assertTrue(self.baseFrame.priority == 0)
        self.assertTrue(self.baseFrame.pos == (0,0))

    def test_intersect(self):
        new_frame_1 = Frame(10, 10, 1, (0, 0))
        new_frame_2 = Frame(10, 5, 1, (11, 11))
        new_frame_3 = Frame(10, 10, 1, (2, 2))
        self.assertFalse(new_frame_1.intersect(new_frame_2))
        self.assertTrue(new_frame_2.intersect(new_frame_3))
        
if __name__ == '__main__':
    unittest.main()
