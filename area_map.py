import random
from entity import *
from utils import *

import tcod.bsp
import tcod.random

map_width = terminal_width
map_height = terminal_height - 5

class Map:
    def __init__(self, name, planet, engine, x, y, w=map_width, h=map_height):
        self.name = name
        self.planet = planet
        self.engine = engine
        self.x = x
        self.y = y
        self.width = w
        self.height = h
        self.player_start_x = self.width // 2
        self.player_start_y = self.height // 2

        self.data = engine.Buffer(self.width, self.height)

        self.entities = []

        self.visibility = [False for _ in range(self.width * self.height)]

        self.generate()

    def generate(self):
        pass

class Settlement(Map):
    def __init__(self, name, planet, engine, x, y, w=map_width, h=map_height):
        super().__init__(name, planet, engine, x, y, w, h)
    
    def generate(self):
        self.engine.Clear(' ', (self.engine.Color.WHITE, self.engine.Color.BACKGROUND), self.data)

        rects = []

        for r in rects:
            self.engine.FillRect('.', (self.engine.Color.GRAY, self.engine.Color.BACKGROUND), r[0], r[1], r[2], r[3], scr = self.data)

        wallify(self.data, self.engine)

        self.engine.ReplaceChar(' ', '.', (self.planet.color_scheme.plains, self.engine.Color.BACKGROUND), scr = self.data)

class Yoore(Settlement):
    def __init__(self, planet, engine, x, y, w=map_width, h=map_height):
        super().__init__("Yoore", planet, engine, x, y, w, h)
        self.entities.append(Zaram(12, 12))

class Shipwreck(Map):
    def __init__(self, name, planet, engine, x, y, w=map_width, h=map_height):
        super().__init__(name, planet, engine, x, y, w, h)
    
    def generate(self):
        model = random.choice(list(self.engine.ship_chassis))
        # model = 'X40'
        self.name = self.name.replace("Test Ship", f'Exodus-{model}')

        s = self.engine.ship_chassis[model]
        self.engine.Clear(' ', (self.engine.Color.WHITE, self.engine.Color.BACKGROUND), scr = self.data)
        self.engine.BlitBuffer(s, x := self.width // 2 - s.width // 2, y := self.height // 2 - s.height // 2, scr=self.data)

        self.engine.ReplaceChar(' ', '.', (self.planet.color_scheme.plains, self.engine.Color.BACKGROUND), scr = self.data)

        self.entities = s.entities

        for e in self.entities:
            e.x += x
            e.y += y
        
        for _ in range(5):
            self.entities.append(Rat(random.randint(0, self.width - 1), random.randint(0, self.height - 1)))

class Dungeon(Map):
    def __init__(self, name, planet, engine, x, y, w=map_width, h=map_height):
        super().__init__(name, planet, engine, x, y, w, h)
    
    def generate(self):
        pass

class Cave(Map):
    def __init__(self, name, planet, engine, x, y, w=map_width, h=map_height):
        super().__init__(name, planet, engine, x, y, w, h)
    
    def generate(self):
        pass

class Base(Map):
    def __init__(self, name, planet, engine, x, y, w=map_width, h=map_height):
        super().__init__(name, planet, engine, x, y, w, h)

        self.level = 1

        self.exp = 0
        self.exp_to_level_up = 5
    
    def generate(self):
        self.engine.Clear('.', (self.planet.overworld.GetAt(self.x, self.y).fg, self.engine.Color.BACKGROUND), self.data)