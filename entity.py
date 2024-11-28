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

        self.move_interact_time = 100

        self.waited_time = 0

    def PlayerMoveInteract(self, engine, player):
        pass

    def OnMyTurn(self, engine):
        pass

# ==============================================================================================================

class ShipPart(Entity):
    def __init__(self, char, c_pair, x, y):
        super().__init__(char, c_pair, x, y)

        self.solid = True

        self.move_interact_time = 0

    def PlayerMoveInteract(self, engine, player):
        engine.AddMessage(f"You bonked the {self.name}! You bastard!")

class ControlPanel(ShipPart):
    def __init__(self, x, y):
        super().__init__("M", (PyneEngine.Color.LIGHT_CYAN, PyneEngine.Color.BACKGROUND), x, y)

        self.name = "Control Panel"

class Door(Entity):
    def __init__(self, x, y, locked = False, char = None, c_pair = None):
        super().__init__(char if char else '+', c_pair if c_pair else (PyneEngine.Color.BROWN, PyneEngine.Color.BACKGROUND), x, y)
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

# ==============================================================================================================

class BasicEnemy(Entity):
    def __init__(self, hp, max_hp, name, chance_to_dodge, x, y, char, c_pair):
        super().__init__(char, c_pair, x, y)

        self.hp     = hp
        self.max_hp = max_hp

        self.name = name

        self.chance_to_dodge = chance_to_dodge

        self.is_enemy = True

        self.speed = 175

        self.move_interact_time = 100 # time to attack

    def Kill(self):
        self.to_remove = True

    def PlayerMoveInteract(self, engine, player):
        player.AttackMelee(self)

    def OnMyTurn(self, engine):
        while self.waited_time >= self.speed:
            self.waited_time -= self.speed
            
            self.OnMove(engine)

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

class CrazedHuman(BasicEnemy):
    def __init__(self, x, y):
        super().__init__(30, 30, "Crazed Human", 0.1, x, y, 'c', (PyneEngine.Color.LIGHT_YELLOW, PyneEngine.Color.BACKGROUND))
        
class Rat(BasicEnemy):
    def __init__(self, x, y):
        super().__init__(30, 30, "Rat", 0.1, x, y, 'r', (PyneEngine.Color.BROWN, PyneEngine.Color.BACKGROUND))

# ==============================================================================================================

class Player:
    def __init__(self, engine, x, y):
        self.engine = engine

        self.x = x
        self.y = y

        self.credits = 1000

        self.endurance = 5
        self.dexterity = 5
        self.intelligence = 5
        self.perception = 5
        self.strength = 5

        self.sight_distance = 10 + self.perception

        self.melee_weapon = MeleeWeapon("Club", MeleeWeaponType.BLUNT, Roll(1, 4, self.strength))

        self.speed = 100

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

# ==============================================================================================================

class NPC(Entity):
    def __init__(self, name, dialogue, color, x, y):
        super().__init__('@', (color, PyneEngine.Color.BLACK), x, y)
        self.name = name

        d = [[self.name] + x for x in dialogue]

        self.dialogue = d
    
        self.is_enemy = False

        self.move_interact_time = 100 # time to talk

    def Kill(self):
        self.to_remove = True

    def PlayerMoveInteract(self, engine, player):
        for t in self.dialogue:
            engine.dialogue_manager.queue_text(t)
    
    def OnMyTurn(self, engine):
        # TODO FIX THIS + IMPLEMENT UNIVERSAL COLLISION DETECTION
        direction = random.randint(0, 3)
        match direction:
            case 0:
                self.y -=1
            case 1:
                self.x += 1
            case 2:
                self.y += 1
            case 3:
                self.x -= 1

class Zaram(NPC):
    def __init__(self, x, y):
        super().__init__("Zaram", 
                        [
                            [
                                "Hello, traveler.",
                                "I am Zaram, and this is Yoore.",
                                "We are a humble community that pride ourselves",
                                "on our hunting and gathering abilities."
                            ],
                            [
                                "What's this?"
                                "... You wish to leave XA-B1-12?",
                                "In that case you will need a ship, my friend."
                            ],
                            [
                                "The easiest way to get a ship is to build one, I'm",
                                "afraid. You'll need to scavenge the parts from the",
                                "various shipwrecks scattered across the surface"
                            ],
                            [
                                "If you are up for the task, I can point you in the",
                                "direction of the nearest one. Be warned, however,",
                                "that a shipwreck is a dangerous place. Many",
                                "unsavory individuals tend to find refuge within",
                                "them."
                            ],
                            [
                                "I wish you good luck on your travels, my friend!"
                            ]
                        ], PyneEngine.Color.LIGHT_RED, x, y)