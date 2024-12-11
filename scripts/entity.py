from pyne.pyne import *
import tcod.path
import numpy as np
from .item import *
from copy import copy
from .utils import *

class Entity:
    def __init__(self, name, char, c_pair, x, y):
        self.repr = ScrElement(char, c_pair[0], c_pair[1])
        
        self.x = x
        self.y = y

        self.name = name

        self.solid = False

        self.is_enemy = False

        self.path = None

        self.to_remove = False

        self.move_interact_time = 100

        self.waited_time = 0

        self.drops = []

    def PlayerMoveInteract(self, engine, player):
        pass

    def PlayerKeyInteract(self, engine, player, key):
        pass

    def OnShoot(self, player):
        pass

    def OnMyTurn(self, engine):
        pass

# ==============================================================================================================

class ShipPart(Entity):
    def __init__(self, name, char, c_pair, x, y):
        super().__init__(name, char, c_pair, x, y)

        self.solid = True

        self.move_interact_time = 0

    def PlayerMoveInteract(self, engine, player):
        engine.AddMessage(f"You bonked the {self.name}! You bastard!")

class ControlPanel(ShipPart):
    def __init__(self, x, y):
        super().__init__("Control Panel", "M", (PyneEngine.Color.LIGHT_CYAN, PyneEngine.Color.BACKGROUND), x, y)

class Door(Entity):
    def __init__(self, x, y, locked = False, char = None, c_pair = None):
        super().__init__("Door", char if char else '+', c_pair if c_pair else (PyneEngine.Color.BROWN, PyneEngine.Color.BACKGROUND), x, y)
        self.locked = locked
        self.solid = True
        self.og_char = copy(char)

        self.move_interact_time = 100 # time to open door

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
        super().__init__(x, y, locked, '%', (PyneEngine.Color.GRAY, PyneEngine.Color.BACKGROUND))
        self.name = "Hatch"

class AreaEntrance(Entity):
    def __init__(self, area, x, y):
        super().__init__("Entrance", ">", (PyneEngine.Color.WHITE, PyneEngine.Color.BACKGROUND), x, y)
        self.area = area

    def PlayerMoveInteract(self, engine, player):
        pass

    def PlayerKeyInteract(self, engine, player, key):
        if key == '>':
            engine.LoadMap(self.area)

# ==============================================================================================================

class BasicEnemy(Entity):
    def __init__(self, hp, max_hp, name, chance_to_dodge, x, y, damage, speed, drops, char, c_pair):
        super().__init__(name, char, c_pair, x, y)

        self.solid = True

        self.hp     = hp
        self.max_hp = max_hp

        self.damage = damage

        self.speed = speed

        self.chance_to_dodge = chance_to_dodge

        self.is_enemy = True

        self.move_interact_time = 100 # time to attack

        self.drops = drops

    def Kill(self):
        self.to_remove = True

    def PlayerMoveInteract(self, engine, player):
        player.AttackMelee(self)

    def OnShoot(self, engine, player):
        player.AttackRanged(self)

    def OnMyTurn(self, engine):
        while self.waited_time >= self.speed:
            self.waited_time -= self.speed
            
            self.OnMove(engine)

            if abs(self.x - engine.player.x) <= 1 and abs(self.y - engine.player.y) <= 1:
                engine.player.AttemptToDamage(self.name, self.damage + random.randint(-1, 1))

    def OnMove(self, engine):
        solids = engine.solids

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
            if issubclass(type(other), BasicEnemy) and other != self:
                if abs(other.x - self.x) <= 1 and abs(other.y - self.y) <= 1:
                    separation_x += self.x - other.x
                    separation_y += self.y - other.y
        
        if total_others:
            separation_x /= total_others
            separation_y /= total_others

        force_x = int(force_x + separation_x)
        force_y = int(force_y + separation_y)

        if 0 <= self.x + force_x <= engine.current_map.width  - 1 and solids[self.x + force_x, self.y]:
            self.x += force_x
        if 0 <= self.y + force_y <= engine.current_map.height - 1 and solids[self.x, self.y + force_y]:
            self.y += force_y
    
class Rat(BasicEnemy):
    def __init__(self, x, y):
        super().__init__(15, 15, "Rat", 0.1, x, y, 5, 120, [RatCorpse], 'r', (PyneEngine.Color.BROWN, PyneEngine.Color.BACKGROUND))

class RockDemon(BasicEnemy):
    def __init__(self, x, y):
        super().__init__(30, 30, "Rock Demon", 0.1, x, y, 10, 150, [Rock], 'R', (PyneEngine.Color.GRAY, PyneEngine.Color.BACKGROUND))

# ===============================================================================================
class ItemPickup(Entity):
    def __init__(self, item, x, y):
        super().__init__(item.name, item.char, (item.color, PyneEngine.Color.BACKGROUND), x, y)
        self.item = item
    
    def PlayerKeyInteract(self, engine, player, key):
        if key == 'p':
            if player.CanPickupItem():
                player.GiveItem(self.item)
                engine.AddMessage(f"Picked up the {self.item.name}.", PyneEngine.Color.LIGHT_GREEN)
                
                self.to_remove = True
                engine.current_map.entities.remove(self)

                engine.advance_time = True
                engine.action_time = action_times[Actions.PICKUP]
            else:
                engine.AddMessage("Insufficient space.", PyneEngine.Color.LIGHT_YELLOW)