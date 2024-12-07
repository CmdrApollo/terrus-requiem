import random
from entity import *
from utils import *

import tcod.bsp
import tcod.random

map_width = terminal_width
map_height = terminal_height - 5

class Map:
    def __init__(self, name, engine, x, y, w=map_width, h=map_height):
        self.name = name
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

class MainMap(Map):
    def __init__(self, engine, w=map_width, h=map_height):
        super().__init__("Shipwreck of the Exodus Z800", engine, engine.TerminalWidth() // 2, engine.TerminalHeight() // 2, w, h)

    def generate(self):
        self.engine.FillRect('.', (self.engine.Color.GRAY, self.engine.Color.BLACK), 0, 0, self.data.width, self.data.height, self.data)

class Cave(Map):
    def __init__(self, name, engine, x, y, w=map_width, h=map_height):
        super().__init__(name, engine, x, y, w, h)
    
    def generate(self):
        pass