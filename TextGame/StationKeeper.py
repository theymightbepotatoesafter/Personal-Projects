"""
Station Keeper v0.4

Author  : Christian Carter
Date    : 2 Oct 2021

Base game code for Station Keeper. Powered by DisplayEngine.py
"""
version_info = 'v0.4'

from Display import Cell, Frame, Sprite, Scene
from DisplayEngine import *
from InputScreen import get_input, check_input

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

class InventoryFull(Exception):
    def __init__(self, character: 'Character'):
        self.char = character
    def __str__(self):
        return f'{self.char} has no more inventory space!'

class Character(Sprite):
    """ Character last name should be variable name\n
        body_stats = (hunger, hunger_max, hunger_mult, sleep, base_fright)\n
        stats = (strength, dexterity, intelligence)    
    """
    def __init__(self, last_name:str, first_name: str, age: float, pronouns: Tuple[str, str, str], pos: Tuple[int, int],
    body_stats: Tuple[float, float, float, float, float], stats: Tuple[int, float, float]):
        # hunger = food bar
        # hunger_max = max food bar
        # hunger_mult = food bar decreased per update
        # sleep =  level of sleep character is at. Affects dex and int
        # base_fright = lowest level of fright character can be at
        # str = how many inventory slots they have
        # dex = how likely they are to succeed at performing a task
        # int = how quickly they are able solve int tasks. Affects how quickly fright rises
        self.last = last_name
        log.debug(self.last)
        self.first = first_name
        self.age = age
        self.pronouns = pronouns
        self.x, self.y = pos
        super().__init__((1, 1), self.last[0].upper(), (self.x, self.y), first_name)
        self.hunger, self.max_hunger, self.hunger_multiplier, self.sleep, self.base_fright = body_stats
        self.str, self.dex, self.int = stats     
        self.inventory = []
        self.walk_speed = round((self.sleep * self.str) + self.dex)
        self.run_speed = round(self.dex * self.sleep * self.str)
        self.fright = 0
        self.scared_state = False
        self.passable = True

    def __repr__(self):
        return f'{self.last}, {self.first[0]}'

    def set_inventory(self, items: List['Item']) -> bool:
        """ Trys to set the inventory of the character. If able to set True is returned """
        if len(self.inventory) == self.str:
            raise InventoryFull(self)
        for item in items:
            if item.weight > (self.str - len(self.inventory)):
                raise InventoryFull
            else:
                self.inventory.append(item)
                return True

    def eat(self, item_no: int):
        """ Eat the item in inventory slot item_no """
        food_item: Food = self.inventory.pop(item_no)
        assert isinstance(food_item, Food), 'Can\'t eat non-food item'
        self.hunger += food_item.replenish()
        if self.hunger > self.max_hunger:
            self.hunger = self.max_hunger

    def sleep_time(self, time: float):
        self.sleep += time

    def update(self):
        self.hunger -= self.hunger_multiplier
        self.sleep -= (self.base_fright / self.int)
        if self.scared_state == True:
            self.fright += (self.fright / (self.int * self.sleep))
        if self.scared_state == False:
            self.fright -= (self.fright / (self.int * self.sleep))
            if self.fright < 0:
                self.fright = 0

class Item(object):
    """ Items that can be placed in the inventory """
    def __init__(self, name: str, weight: int):
        self.name = name
        self.weight = weight

    def get(self, character: Character) -> bool:
        """ Tries to put item in character's inventory, returns if they did or not """
        try:
            character.set_inventory([self])
            return True
        except InventoryFull as e:
            return False

class Food(Item):
    """ Food item can be eaten or drunk """
    def __init__(self, name: str, weight: int, hunger: float):
        super().__init__(name, weight)
        self.hunger = hunger    # Hunger restored

    def replenish(self) -> float:
        return self.hunger

class Wall(Sprite):
    def __init__(self, size: Tuple[int, int], chars: str, pos: Tuple[int, int], name = 'Wall'):
        super().__init__(size, chars, pos, name)
        self.passable = False
    
    def change_pos(self, new_pos: Tuple[int, int]):
        self.x, self.y = new_pos

    def __str__(self):
        return self.name

class Corner(Wall):
    def __init__(self, size: Tuple[int, int], chars: str, pos: Tuple[int, int]):
        super().__init__(size, '#', pos, 'Corner')

class SceneEditor(Scene):

    def __init__(self, scene: Scene, to_display: Instance, bg_str: str = ' '):
        self.view = False
        self.scene = scene
        self.queue = to_display
        self.sprites: List[Sprite] = []
        for sprite in self.scene.sprites:
            self.sprites.append(sprite)
        self.characters: List[Character] = []
        self.background = bg_str
        self.name = 'scene_editor'

    def set_view(self, view_state):
        self.view = view_state
        if view_state:
            self.update()

    def update(self, to = 'display0'):
        self.queue.instruction_put(Instruction('update', to = to))

    def make_wall(self, size_x: int, size_y: int, pos_x: int, pos_y: int):
        if size_x > size_y:
            chars = '='
        else:
            chars = '||'
        wall = Wall((size_y, size_x), chars, (pos_x, pos_y))
        self.scene.put_sprite(wall)
        self.sprites.append(wall)
        if self.view:
            self.queue.instruction_put(Instruction('putFrame', (self.scene, ), 'display0'))
            self.update('display0')

    def make_sprite(self, size_x, size_y, chars, pos_x, pos_y):
        new_sprite = Sprite((size_y, size_x), chars, (pos_x, pos_y))
        self.scene.put_sprite(new_sprite)
        self.sprites.append(new_sprite)
        if self.view:
            self.queue.instruction_put(Instruction('putFrame', (self.scene, ), 'display0'))
            self.update('display0')

    def get_sprites(self) -> List:
        return self.sprites + self.characters

    def put_sprite(self, sprite: str):
        for sprite_num in range(self.sprites):
            if self.sprites[sprite_num].name == sprite:
                self.scene.put_sprite(self.sprites[sprite_num])
        if self.view:
            self.queue.instruction_put(Instruction('putFrame', (self.scene, ), 'display0'))
            self.update('display0')

    def add_character(self, character: Character):
        self.characters.append(character)
        self.scene.put_sprite(character)
        if self.view:
            self.queue.instruction_put(Instruction('putFrame', self.scene, 'display0'))
            self.update('display0')

    def make_character(self):
        pass

    def move_character(self, first_name: str, pos_x: int, pos_y: int):
        for character in self.characters:
            if character.first == first_name:
                self.scene.cells[character.y][character.x].set_value(self.background)
                self.scene.cells[character.y + pos_y][character.x + pos_x].set_value(character.string)
        if self.view:
            self.queue.instruction_put(Instruction('putFrame', (self.scene, ), 'display0'))
            self.update('display0')

def instruction_handle(instruction):
    log.debug(f'Write code to handle instruction you nut\n{instruction}')

def instruction_loop(queue: Queue):
    while True:
        try:
            put: Instruction = queue.get(True)
            if put.destination() != 'game':
                game.instruction_put(put)
                continue
            instruction_handle(put)
        except Empty:
            log.debug('Queue is empty...')
            continue

if __name__ == '__main__':
    ctx = get_context()
    queue = Queue(20, ctx = ctx)
    size = (50, 180)
    game = Instance('Station Keeper', size, queue, 0.01, 2)
    game.hide_logs()
    game.default_start()
    get = Process(target = instruction_loop, args = (queue, ))
    get.start()
    
    Jones = Character('Jones', 'A', 54, ('he', 'him', 'his'), (1, 1), (15.0, 20.0, .1, 0.99, 0),(10, 10.0, 6.5))
    test_scene = Scene(size, [])
    scene_edit = SceneEditor(test_scene, game)
    scene_edit.add_character(Jones)
    scene_edit.update('display0')

    VALID_INSTRUCTION = ['putSprite',
                         'makeSprite', 
                         'makeCharacter',
                         'makeWall',
                         'listSprites', 
                         'setView',
                         'moveCharacter']

    TASK = {
        'putSprite': scene_edit.put_sprite,
        'makeSprite': scene_edit.make_sprite,
        'makeCharacter': scene_edit.make_character,
        'makeWall': scene_edit.make_wall,
        'listSprites': scene_edit.get_sprites,
        'moveCharacter': scene_edit.move_character,
        'setView': scene_edit.set_view
    }

    message = 'Input: '
    log.debug(TASK)
    while True:
        instruction: List = check_input(get_input(message), VALID_INSTRUCTION)
        message = 'Input: '
        if instruction[0] in VALID_INSTRUCTION:
            task = instruction.pop(0)
            if task == 'makeWall':
                try:
                    log.debug(TASK[task])
                    var_1 = int(instruction[0])
                    var_2 = int(instruction[1])
                    var_3 = int(instruction[2])
                    var_4 = int(instruction[3])
                    TASK[task](var_1, var_2, var_3, var_4)
                except IndexError as e:
                    message = 'makeWall needs 4 arguments\nInput: '
                    log.debug(e)
                continue
            if task == 'listSprites':
                message = str(TASK[task]()) + '\nInput:'
                continue
            if task == 'moveCharacter':
                try:
                    TASK[task](
                        instruction[0],
                        int(instruction[1]),
                        int(instruction[2])
                    )
                except IndexError as e:
                    message = 'moveCharacter needs 3 arguments\nInput: '
                continue
            if task == 'setView':
                if instruction[0].lower() == 'true':
                    view_bool = True
                else:
                    view_bool = False
                TASK[task](view_bool)
                continue

        
