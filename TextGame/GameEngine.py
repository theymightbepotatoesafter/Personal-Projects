"""
Game Engine v0.1

Author  : Christian Carter
Date    : 10 June 2021

Code for mkaing all of the other code talk to eachother.
"""
version_info = "v0.2"
from typing import Dict
from Display import *
from IO import *

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

class GameInstance(object):

    def __init__(self, size_screen: Tuple[int, int]):
        """
            A GameInstance object is the backbone of the game.
            It routs Instruction objects to and from the Input 
            and Output cmdDisplay objects. It essentially fun-
            ctions as the hardware the game is played on.
            """
        self.__path = os.getcwd()
        self.display_screen_count: int = -1
# Display_0 = cmdDisplay(size_screen[0], size_screen[1], 10, cls = self)
        self.displays: Dict[int, Output] = {}
        self.size = size_screen
        
        #########################
        #
        #  Start the server for the information passing here
        #  instead of doing it through IO
        #
        #########################

        # one display screen, for now
        # one input screen

    def get_display_num(self) -> int:
        self.display_screen_count += 1
        return self.display_screen_count

    def gameStart(self):
        inputScreen = Input(50, 2000)
        display_num = self.get_display_num()
        self.displays[display_num] = Output(50, 2001) 
        self.displays[display_num].send((self.size, display_num))
        
if __name__ == "__main__":
    new_game = GameInstance((100, 100))
    new_game.gameStart()
    while 1:
        continue
