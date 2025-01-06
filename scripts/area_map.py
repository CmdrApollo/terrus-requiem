import random
from .entity import *
from .utils import *

import tcod.bsp

map_width = terminal_width
map_height = terminal_height - 5

RANDOM_ITEM_CHANCE = 0.0025

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

class MainDeck(Map):
    def __init__(self, name, engine, w=map_width, h=map_height):
        super().__init__(name, engine, w // 2 - 1, h // 2 - 3, w, h)

    def generate(self):
        monsters = [Rat, RockDemon]
        items = [
            Club, BasicSpear, AdvancedSpear,
            BasicBlaster, AdvancedBlaster,
            LightArmor, MediumArmor, HeavyArmor
        ]
        max_items_per_room = 3

        self.engine.FillRect(' ', (self.engine.Color.DARK_GRAY, self.engine.Color.BACKGROUND), 0, 0, self.data.width, self.data.height, self.data)

        bsp = tcod.bsp.BSP(1, 1, self.width - 2, self.height - 2)
        bsp.split_recursive(
            depth=5,
            min_width=24,
            min_height=8,
            max_horizontal_ratio=1,
            max_vertical_ratio=1,
        )

        rects = bsp.pre_order()
        entrancex = -1
        entrancey = -1

        for i, r in enumerate(rects):
            if not r.children:
                x, y, w, h = r.x, r.y, r.width, r.height
                self.engine.FillRect('.', (self.engine.Color.DARK_GRAY, self.engine.Color.BACKGROUND), x + 4, y + 4, w - 8, h - 8, self.data)
                if entrancex == -1:
                    self.player_start_x = entrancex = x + 4 + (w - 8) // 2
                    self.player_start_y = entrancey = y + 4 + (h - 8) // 2

                    self.entities.append(AreaEntrance('caves', entrancex, entrancey))
            else:
                node1, node2 = r.children
                x1, y1, w1, h1 = node1.x, node1.y, node1.width, node1.height
                x2, y2, w2, h2 = node2.x, node2.y, node2.width, node2.height
                x1 += 4 + (w1 - 8) // 2
                x2 += 4 + (w2 - 8) // 2
                y1 += 4 + (h1 - 8) // 2
                y2 += 4 + (h2 - 8) // 2
                mx = (x1 + x2) // 2
                my = (y1 + y2) // 2
                self.engine.DrawVLine((self.engine.Color.DARK_GRAY, self.engine.Color.BACKGROUND), x1, y1, my, '.', self.data)
                self.engine.DrawHLine((self.engine.Color.DARK_GRAY, self.engine.Color.BACKGROUND), x1, my, x2, '.', self.data)
                self.engine.DrawVLine((self.engine.Color.DARK_GRAY, self.engine.Color.BACKGROUND), x2, my, y2, '.', self.data)
                
                self.engine.DrawHLine((self.engine.Color.DARK_GRAY, self.engine.Color.BACKGROUND), x1, y1, mx, '.', self.data)
                self.engine.DrawVLine((self.engine.Color.DARK_GRAY, self.engine.Color.BACKGROUND), mx, y1, y2, '.', self.data)
                self.engine.DrawHLine((self.engine.Color.DARK_GRAY, self.engine.Color.BACKGROUND), mx, y2, x2, '.', self.data)

        wallify(self.data, self.engine, 0)

class Medbay(Map):
    def __init__(self, name, engine, w=map_width, h=map_height):
        super().__init__(name, engine, w // 2 - 1, h // 2 - 3, w, h)

    def generate(self):
        self.engine.FillRect(' ', (self.engine.Color.DARK_GRAY, self.engine.Color.BACKGROUND), 0, 0, self.data.width, self.data.height, self.data)

        self.player_start_x = 10
        self.player_start_y = 12

        self.engine.FillCircle('.', (self.engine.Color.DARK_GRAY, self.engine.Color.BACKGROUND), 16, 12, 10, self.data)
        self.engine.FillCircle('.', (self.engine.Color.DARK_GRAY, self.engine.Color.BACKGROUND), 28, 12, 10, self.data)
        self.engine.FillCircle('.', (self.engine.Color.DARK_GRAY, self.engine.Color.BACKGROUND), 40, 12, 10, self.data)

        self.engine.DrawVLine((self.engine.Color.DARK_GRAY, self.engine.Color.BACKGROUND), 21, 5, 10, ' ', self.data)
        self.engine.DrawVLine((self.engine.Color.DARK_GRAY, self.engine.Color.BACKGROUND), 33, 5, 10, ' ', self.data)
        self.engine.DrawVLine((self.engine.Color.DARK_GRAY, self.engine.Color.BACKGROUND), 21, 15, 20, ' ', self.data)
        self.engine.DrawVLine((self.engine.Color.DARK_GRAY, self.engine.Color.BACKGROUND), 33, 15, 20, ' ', self.data)

        self.entities.append(AreaEntrance('maindeck', 40, 12))

        self.entities.append(ShipLog(0, 12, 6))

        wallify(self.data, self.engine, 0)

class ControlDeck(Map):
    def __init__(self, name, engine, w=map_width, h=map_height):
        super().__init__(name, engine, w // 2 - 1, h // 2 - 3, w, h)

    def generate(self):
        self.engine.FillRect(' ', (self.engine.Color.DARK_GRAY, self.engine.Color.BACKGROUND), 0, 0, self.data.width, self.data.height, self.data)

class Hanger(Map):
    def __init__(self, name, engine, w=map_width, h=map_height):
        super().__init__(name, engine, w // 2 - 1, h // 2 - 3, w, h)

    def generate(self):
        self.engine.FillRect(' ', (self.engine.Color.DARK_GRAY, self.engine.Color.BACKGROUND), 0, 0, self.data.width, self.data.height, self.data)


class Cave(Map):
    def __init__(self, name, engine, danger, w=map_width, h=map_height):
        self.danger = danger
        super().__init__(name, engine, w // 2 - 1, h // 2 - 1, w, h)
    
    def generate(self):
        monsters = [Rat, RockDemon]
        items = [
            Club, BasicSpear, AdvancedSpear,
            BasicBlaster, AdvancedBlaster,
            LightArmor, MediumArmor, HeavyArmor
        ]

        self.engine.FillRect(' ', (self.engine.Color.DARK_GRAY, self.engine.Color.BACKGROUND), 0, 0, self.data.width, self.data.height, self.data)

        x, y = self.width // 2, self.height // 2

        for i in range(3500):
            self.engine.DrawChar('.', (self.engine.Color.DARK_GRAY, self.engine.Color.BACKGROUND), x, y, self.data)
            if i == 0:
                self.entities.append(AreaEntrance('medbay', x, y))
            if i == 1:
                self.entities.append(ShipLog(1, x, y))
            if random.random() <= RANDOM_ITEM_CHANCE:
                self.entities.append(ItemPickup(random.choice(items)(), x, y))
            if random.random() <= self.danger / 1000:
                self.entities.append(random.choice(monsters)(x, y))

            r = random.randint(0, 3)
            c = [[0, -1], [1, 0], [0, 1], [-1, 0]]
            x += c[r][0]
            x = clamp(x, 1, self.width - 2)
            y += c[r][1]
            y = clamp(y, 1, self.height - 2)
        
        wallify(self.data, self.engine, 1)