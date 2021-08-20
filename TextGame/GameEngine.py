"""
Game Engine v0.2

Author  : Christian Carter
Date    : 18 Aug 2021

Code for mkaing all of the other code talk to eachother.
"""
version_info = "v0.2"
from Display import *
from multiprocessing import Process, set_start_method
import InputScreen

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

class GameInstance():

    def __init__(self, screen_size: Tuple[int, int], max_displays: int = 3):
        """
            A GameInstance object is the backbone of the game.
            It routs Instruction objects to and from the Input
            and Output cmdDisplay objects. It essentially funcitons
            as the hardware the game is played on.
        """
        self.__path = os.getcwd()
        self.display_count: int = 0
        self.max_displays = max_displays
        self.input_count: int = 0
        self.size = screen_size
        self.displays: List[Process] = []

    def startGame(self):
        """
            Starts the game from the GameEngine object using the
            multiprocessing library. Each Display and InputScreen
            is a separate process that communicates with the
            GameEngine object
        """
        input_queue = Queue(5)
        output_queue = Queue(5)
        display0 = Process(target = cmdDisplay, args = (self.size[0], self.size[1], output_queue), 
        kwargs = {'name': self.display_count})
        input0 = Process(target = InputScreen.main, args = input_queue)

        # I don't think that the processes will spawn cmd lines.
        # I may need to write some code to pass the processes to 
        # individual cmd lines or completely change the way that
        # the processes are connected, maybe through Pipes as I 
        # did before.

if __name__ == '__main__':
    #set_start_method('forkserver', force = True)
    game = GameInstance((40, 40))
    game.startGame()
