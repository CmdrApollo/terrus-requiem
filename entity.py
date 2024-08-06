from pyne.pyne import *
import tcod.path
import numpy as np
from item import *
from copy import copy

class Entity:
    def __init__(self, char, c_pair, x, y):
        self.repr = ScrElement(char, c_pair[0], c_pair[1])
        
        self.x = x
        self.y = y

        self.solid = False

        self.is_enemy = False

        self.path = None

        self.to_remove = False
    
    def PlayerMoveInteract(self, engine, player):
        pass

    def OnMyTurn(self, engine):
        pass

class Door(Entity):
    def __init__(self, x, y, locked = False, char = None, c_pair = None):
        super().__init__(char if char else '+', c_pair if c_pair else (PyneEngine.Color.BROWN, PyneEngine.Color.BLACK), x, y)
        self.locked = locked
        self.solid = True
        self.og_char = copy(char)

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

class BasicEnemy(Entity):
    def __init__(self, hp, max_hp, name, chance_to_dodge, x, y, char, c_pair):
        super().__init__(char, c_pair, x, y)

        self.hp     = hp
        self.max_hp = max_hp

        self.name = name

        self.chance_to_dodge = chance_to_dodge

        self.is_enemy = True

    def Kill(self):
        self.to_remove = True

    def PlayerMoveInteract(self, engine, player):
        player.AttackMelee(self)

    def OnMyTurn(self, engine):
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

        if 0 <= self.x + force_x <= engine.current_map.width - 1 and solids[self.x + force_x, self.y]:
            self.x += force_x
        if 0 <= self.y + force_y <= engine.current_map.height - 1 and solids[self.x, self.y + force_y]:
            self.y += force_y

class CrazedHuman(BasicEnemy):
    def __init__(self, x, y):
        super().__init__(30, 30, "Crazed Human", 0.1, x, y, 'r', (PyneEngine.Color.LIGHT_YELLOW, PyneEngine.Color.BLACK))

class Player:
    def __init__(self, engine, x, y):
        self.engine = engine

        self.x = x
        self.y = y

        self.sight_distance = 4

        self.scrap = 100
        self.credits = 1000

        self.strength = 5
        self.intelligence = 5
        self.dexterity = 5
        self.perception = 5
        self.endurance = 5

        self.melee_weapon = MeleeWeapon("Club", MeleeWeaponType.BLUNT, Roll(1, 4, self.strength))

    def ChanceToHitMelee(self):
        return + (self.perception / 10)
    
    def AttackMelee(self, entity):
        if random.random() <= self.ChanceToHitMelee():
            # hit successful
            
            if random.random() <= entity.chance_to_dodge:
                # enemy dogdged

                self.engine.AddMessage(f"The {entity.name} dodged your attack!")
            else:
                dmg = self.melee_weapon.roll_damage()

                self.engine.AddMessage(f"You deal {dmg} damage to the {entity.name}!")

                entity.hp -= dmg

                if entity.hp <= 0:
                    self.engine.AddMessage(f"You killed the {entity.name}!")

                    entity.Kill()
        else:
            self.engine.AddMessage(f"You missed the {entity.name}.")