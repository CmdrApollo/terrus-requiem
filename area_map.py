import random
from entity import *

class Map:
    def __init__(self, name, planet, engine, x, y, w=74, h=21):
        self.name = name
        self.planet = planet
        self.engine = engine
        self.x = x
        self.y = y
        self.width = w
        self.height = h

        self.data = engine.Buffer(self.width, self.height)

        self.entities = []

        self.visibility = [False for _ in range(self.width * self.height)]

        self.generate()

    def generate(self):
        pass

class Settlement(Map):
    def __init__(self, name, planet, engine, w=74, h=21):
        super().__init__(name, planet, engine, w, h)
    
    def generate(self):
        pass

class Shipwreck(Map):
    def __init__(self, name, planet, engine, w=74, h=21):
        super().__init__(name, planet, engine, w, h)
    
    def generate(self):
        # model = random.choice(list(self.engine.ship_chassis))
        model = 'X40'
        self.name = self.name.replace("Test Ship", f'Exodus-{model}')

        s = self.engine.ship_chassis[model]
        self.engine.Clear(' ', (self.engine.Color.WHITE, self.engine.Color.BLACK), scr = self.data)
        self.engine.BlitBuffer(s, x := self.width // 2 - s.width // 2, y := self.height // 2 - s.height // 2, scr=self.data)

        self.engine.ReplaceChar(' ', '.', (self.planet.color_scheme.plains, self.engine.Color.BLACK), scr = self.data)

        self.entities = s.entities

        for e in self.entities:
            e.x += x
            e.y += y
        
        for _ in range(5):
            self.entities.append(Enemy(random.randint(0, self.width - 1), random.randint(0, self.height - 1), 'e', (self.engine.Color.LIGHT_RED, self.engine.Color.BLACK)))

class Dungeon(Map):
    def __init__(self, name, planet, engine, w=74, h=21):
        super().__init__(name, planet, engine, w, h)
    
    def generate(self):
        pass

class Cave(Map):
    def __init__(self, name, planet, engine, w=74, h=21):
        super().__init__(name, planet, engine, w, h)
    
    def generate(self):
        pass

class Base(Map):
    def __init__(self, name, planet, engine, x, y, w=74, h=21):
        super().__init__(name, planet, engine, x, y, w, h)

        self.level = 1

        self.exp = 0
        self.exp_to_level_up = 5
    
    def generate(self):
        self.engine.Clear('.', (self.planet.overworld.GetAt(self.x, self.y).fg, self.engine.Color.BLACK), self.data)