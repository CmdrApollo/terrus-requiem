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
        super().__init__("Shipwreck of the Exodus Z800", engine, engine.TerminalWidth() // 2 - 1, engine.TerminalHeight() // 2 - 3, w, h)

class ShipArea(Map):
    def __init__(self, name, engine, danger=0, w=map_width, h=map_height):
        super().__init__(name, engine, engine.TerminalWidth() // 2 - 1, engine.TerminalHeight() // 2 - 3, w, h)
        self.danger = danger

    def generate(self):
        self.engine.FillRect(' ', (self.engine.Color.DARK_GRAY, self.engine.Color.BLACK), 0, 0, self.data.width, self.data.height, self.data)

        rects = []
        entrancex = -1
        entrancey = -1

        for i in range(3):
            for j in range(3):
                if random.random() <= 0.5:
                    x, y, w, h = i * (self.data.width // 3) + self.data.width // 6, j * (self.data.height // 3) + self.data.height // 6, random.randint(8, 12), random.randint(3, 4)
                    self.engine.FillRect('.', (self.engine.Color.DARK_GRAY, self.engine.Color.BLACK), x - w // 2, y - h // 2, w, h, self.data)

                    v = random.random()
                    if v <= 0.5:
                        # place an enemy in the room
                        self.entities.append(random.choice([Rat, Chimp])(x, y))
                    elif v <= 1 and entrancex == -1:
                        entrancex = x - w // 2 + random.randint(0, w - 1)
                        entrancey = y - h // 2 + random.randint(0, h - 1)

                        self.player_start_x = entrancex
                        self.player_start_y = entrancey

                        self.entities.append(AreaEntrance(entrancex, entrancey))

        connections = [
            ((0, 0), (1, 0)),
            ((1, 0), (2, 0)),
            ((0, 0), (0, 1)),
            ((0, 1), (1, 1)),
            ((1, 1), (2, 1)),
            ((0, 1), (0, 2)),
            ((0, 2), (1, 2)),
            ((1, 2), (2, 2)),
            ((1, 0), (1, 1)),
            ((2, 0), (2, 1)),
            ((1, 1), (1, 2)),
            ((2, 1), (2, 2))
        ]

        for c in connections:
            i1 = c[0][0]
            j1 = c[0][1]
            i2 = c[1][0]
            j2 = c[1][1]

            x1, y1 = i1 * (self.data.width // 3) + self.data.width // 6, j1 * (self.data.height // 3) + self.data.height // 6
            x2, y2 = i2 * (self.data.width // 3) + self.data.width // 6, j2 * (self.data.height // 3) + self.data.height // 6

            if x1 == x2:
                self.engine.DrawVLine((self.engine.Color.DARK_GRAY, self.engine.Color.BLACK), x1, y1, y2, '.', self.data)
            else:
                self.engine.DrawHLine((self.engine.Color.DARK_GRAY, self.engine.Color.BLACK), x1, y1, x2 + 1, '.', self.data)

        wallify(self.data, self.engine, 0)

class Cave(Map):
    def __init__(self, name, engine, x, y, w=map_width, h=map_height):
        super().__init__(name, engine, x, y, w, h)
    
    def generate(self):
        pass