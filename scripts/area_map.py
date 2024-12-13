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

class ShipArea(Map):
    def __init__(self, name, engine, danger=0, w=map_width, h=map_height):
        super().__init__(name, engine, w // 2 - 1, h // 2 - 3, w, h)
        self.danger = danger

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
            min_width=3,
            min_height=3,
            max_horizontal_ratio=1.5,
            max_vertical_ratio=1.5,
        )

        rects = bsp.pre_order()
        entrancex = -1
        entrancey = -1
        
        for r in rects:
            if not r.children:
                x, y, w, h = r.x, r.y, r.width, r.height
                self.engine.FillRect('.', (self.engine.Color.DARK_GRAY, self.engine.Color.BACKGROUND), x - w // 2, y - h // 2, w, h, self.data)
            else:
                node1, node2 = r.children
                x1, y1, w1, h1 = node1.x, node1.y, node1.width, node1.height
                x2, y2, w2, h2 = node2.x, node2.y, node2.width, node2.height

        # for i in range(4):
        #     for j in range(4):
        #         if random.random() <= 0.5:
        #             x, y, w, h = i * (self.data.width // 4) + self.data.width // 8, j * (self.data.height // 4) + self.data.height // 8, random.randint(24, 36), random.randint(12, 16)
        #             self.engine.FillRect('.', (self.engine.Color.DARK_GRAY, self.engine.Color.BACKGROUND), x - w // 2, y - h // 2, w, h, self.data)

        #             for _ in range(random.randint(0, max_items_per_room)):
        #                 self.entities.append(ItemPickup(random.choice(items)(), x + random.randint(-1, 1), y + random.randint(-1, 1)))
        #             v = random.random()
        #             if v <= 0.5:
        #                 # place an enemy in the room
        #                 self.entities.append(random.choice(monsters)(x, y))
        #             elif v <= 1 and entrancex == -1:
        #                 entrancex = x - w // 2 + random.randint(0, w - 1)
        #                 entrancey = y - h // 2 + random.randint(0, h - 1)

        #                 self.player_start_x = entrancex
        #                 self.player_start_y = entrancey

        #                 self.entities.append(AreaEntrance('caves', entrancex, entrancey))

        # connections = [
        #     ((0, 0), (1, 0)),
        #     ((1, 0), (2, 0)),
        #     ((0, 0), (0, 1)),
        #     ((0, 1), (1, 1)),
        #     ((1, 1), (2, 1)),
        #     ((0, 1), (0, 2)),
        #     ((0, 2), (1, 2)),
        #     ((1, 2), (2, 2)),
        #     ((1, 0), (1, 1)),
        #     ((2, 0), (2, 1)),
        #     ((1, 1), (1, 2)),
        #     ((2, 1), (2, 2))
        # ]

        # for c in connections:
        #     i1 = c[0][0]
        #     j1 = c[0][1]
        #     i2 = c[1][0]
        #     j2 = c[1][1]

        #     x1, y1 = i1 * (self.data.width // 4) + self.data.width // 8, j1 * (self.data.height // 4) + self.data.height // 8
        #     x2, y2 = i2 * (self.data.width // 4) + self.data.width // 8, j2 * (self.data.height // 4) + self.data.height // 8

        #     if x1 == x2:
        #         self.engine.DrawVLine((self.engine.Color.DARK_GRAY, self.engine.Color.BACKGROUND), x1, y1, y2, '.', self.data)
        #     else:
        #         self.engine.DrawHLine((self.engine.Color.DARK_GRAY, self.engine.Color.BACKGROUND), x1, y1, x2 + 1, '.', self.data)

        wallify(self.data, self.engine, 0)

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
                self.entities.append(ShipLog(0, x, y))
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