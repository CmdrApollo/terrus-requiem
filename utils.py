import random
from pyne.pyne import *

class Actions:
    CLOSE_DOOR = 0
    MELEE_ATTACK = 1
    RANGED_ATTACK = 2
    PICKUP = 3

action_times = [ 75, 100, 50, 100 ]

from entity import *

terminal_width, terminal_height = 88, 36
MAPWIDTH, MAPHEIGHT = 200, 80

def string_to_seed(string):
    return int(sum([ord(string[i]) for i in range(len(string))]))

def wallify(buffer, engine, colorscheme=0):
    schemes = [
        [engine.Color.GRAY, engine.Color.DARK_GRAY] * 2 + [engine.Color.LIGHT_BLUE],    # ship
        [engine.Color.BROWN, engine.Color.DARK_BROWN, engine.Color.VERY_DARK_RED] * 2 + [engine.Color.GRAY], # caves
    ]

    neighbors = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, 1), (1, 1), (1, -1), (-1, -1)]

    for x in range(buffer.width):
        for y in range(buffer.height):
            if buffer.GetAt(x, y).symbol == ' ':
                for n in neighbors:
                    el = buffer.GetAt(x + n[0], y + n[1])
                    if el and el.symbol == '.':
                        engine.DrawChar('#', (engine.Color.BACKGROUND, random.choice(schemes[colorscheme])), x, y, buffer)
                        break

    for x in range(buffer.width):
        for y in range(buffer.height):
            if buffer.GetAt(x, y).symbol == ' ':
                engine.DrawChar('.', (engine.Color.DARK_GRAY, engine.Color.BACKGROUND), x, y, buffer)

def crop(buffer, engine):
    min_x, max_x = 0xffff, 0
    min_y, max_y = 0xffff, 0
    
    for x in range(buffer.width):
        for y in range(buffer.height):
            if buffer.GetAt(x, y).symbol != ' ':
                if x < min_x: min_x = x
                if x > max_x: max_x = x
                if y < min_y: min_y = y
                if y > max_y: max_y = y
    
    max_x += 1
    max_y += 1

    new_buffer = BufferWithEntities(max_x - min_x, max_y - min_y)

    for x in range(new_buffer.width):
        for y in range(new_buffer.height):
            e = buffer.GetAt(min_x + x, min_y + y)
            engine.DrawChar(e.symbol, (e.fg, e.bg), x, y, scr=new_buffer)
    
    new_buffer.entities = buffer.entities.copy()

    return new_buffer

def clamp(x, minv, maxv):
    return min(max(minv, x), maxv)

class BufferWithEntities(PyneEngine.Buffer):
    def __init__(self, width: int, height: int):
        super().__init__(width, height)

        self.entities: list[Entity] = []