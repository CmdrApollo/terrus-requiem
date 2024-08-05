from pyne.pyne import *
import tcod.path
import numpy as np

class Entity:
    def __init__(self, char, c_pair, x, y):
        self.repr = ScrElement(char, c_pair[0], c_pair[1])
        
        self.x = x
        self.y = y

        self.solid = False

        self.is_enemy = False

        self.path = None
    
    def PlayerMoveInteract(self, engine, player):
        pass

    def OnMyTurn(self, engine):
        pass

class Door(Entity):
    def __init__(self, x, y, locked = False, char = None, c_pair = None):
        super().__init__(char if char else '+', c_pair if c_pair else (PyneEngine.Color.BROWN, PyneEngine.Color.BLACK), x, y)
        self.locked = locked
        self.solid = True
        self.og_char = char

    def PlayerMoveInteract(self, engine, player):
        if self.repr.symbol == '/':
            player.x = self.x
            player.y = self.y
        elif not self.locked:
            self.repr.symbol = '/'
            self.solid = False
    
    def Close(self):
        self.repr.symbol = self.og_char

        self.solid = True

class Hatch(Door):
    def __init__(self, x, y, locked = False):
        super().__init__(x, y, locked, '%', (PyneEngine.Color.GRAY, PyneEngine.Color.BLACK))

class Enemy(Entity):
    def __init__(self, x, y, char, c_pair):
        super().__init__(char, c_pair, x, y)

        self.hp     = 100
        self.max_hp = 100

        self.name = "Basic Enemy"

        self.is_enemy = True

    def PlayerMoveInteract(self, engine, player):
        engine.AddMessage(f"Player Hit {self.name}!")

    def OnMyTurn(self, engine):
        solids: np.Arrayterator = engine.solids

        solids = np.transpose(solids, (1, 0))

        graph = tcod.path.SimpleGraph(cost=solids, cardinal=2, diagonal=3,)

        finder = tcod.path.Pathfinder(graph)

        finder.add_root((self.x, self.y))

        my_path = finder.path_to((engine.player.x, engine.player.y))
        
        my_path = my_path.tolist()[1:-1]

        self.path = my_path

        force_x = force_y = 0

        if len(my_path) > 1:

            force_x = my_path[0][0] - self.x
            force_y = my_path[0][1] - self.y

        separation_x = 0
        separation_y = 0

        total_others = 0

        for other in engine.current_map.entities:
            if other != self:
                if abs(other.x - self.x) <= 1 and abs(other.y - self.y) <= 1:
                    separation_x += self.x - other.x
                    separation_y += self.y - other.y
        
        if total_others:
            separation_x /= total_others
            separation_y /= total_others

        force_x = int(force_x + separation_x)
        force_y = int(force_y + separation_y)

        if 0 <= self.x + force_x <= engine.current_map.width - 1 and solids[self.x + force_x, self.y]:
            self.x += force_x
        if 0 <= self.y + force_y <= engine.current_map.height - 1 and solids[self.x, self.y + force_y]:
            self.y += force_y

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y

        self.sight_distance = 4

        self.scrap = 100
        self.credits = 1000