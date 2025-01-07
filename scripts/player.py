from .item import *
from .utils import *
import math

class PlayerStats:
    ENDURANCE = 0
    DEXTERITY = 1
    INTELLIGENCE = 2
    PERCEPTION = 3
    STRENGTH = 4

class Player:
    def __init__(self, engine, x, y):
        self.engine = engine

        self.x = x
        self.y = y

        self.stats = [5, 5, 5, 5, 5]

        self.melee_weapon = None
        self.ranged_weapon = None
        self.armor = None

        self.CalculateStats()

        self.firing = False
        self.heading = 0
        self.projx = 0
        self.projy = 0

        self.inventory = []

        self.pickup_chance = 0.5

    def CalculateStats(self):
        self.sight_distance = 5 + self.stats[PlayerStats.PERCEPTION]

        self.speed = 150 - 10 * self.stats[PlayerStats.DEXTERITY]

        self.health = self.max_health = 5 * self.stats[PlayerStats.ENDURANCE] + self.stats[PlayerStats.STRENGTH]

        self.energy = self.max_energy = 100

        self.capacity = 2 * self.stats[PlayerStats.ENDURANCE]

        self.pickup_chance = self.stats[PlayerStats.INTELLIGENCE] / 10

    def CanPickupItem(self):
        return len(self.inventory) < self.capacity

    def GiveItem(self, item):
        self.inventory.append(item)

    def AttemptToDamage(self, name, dmg):
        d = dmg
        if random.randint(1, 10) <= self.stats[PlayerStats.DEXTERITY] - 1:
            self.engine.AddMessage(f"You dodged the attack from the {name}!")
            return
        armor_was_destroyed = False
        if self.armor:
            armor_was_destroyed = self.armor.destroyed
            d = self.armor.FilterDamage(d)
        if d == 0:
            self.engine.AddMessage(f"Your armor protected you from the {name}!")
        else:
            self.health = max(0, self.health - d)
            self.engine.AddMessage(f"The {name} hit you for {d} damage!", PyneEngine.Color.LIGHT_RED)
            if self.armor and not armor_was_destroyed:
                self.engine.AddMessage(f"Your armor ablated!", PyneEngine.Color.LIGHT_RED)
                if self.armor.destroyed:
                    self.engine.AddMessage(f"Your armor was destroyed!", PyneEngine.Color.LIGHT_RED)
            if self.health == 0:
                self.engine.AddMessage(f"You died!", PyneEngine.Color.LIGHT_RED)

                # TODO write this function...
                self.engine.OnGameOver()

    def ChanceToHitMelee(self):
        return + ((self.stats[PlayerStats.PERCEPTION] + 1) / 10)

    def ChanceToHitRanged(self):
        return + ((self.stats[PlayerStats.PERCEPTION] + 1) / 10)
    
    def AttackMelee(self, entity):
        if random.random() <= self.ChanceToHitMelee():
            # hit successful
            
            if random.random() <= entity.chance_to_dodge:
                # enemy dogdged

                self.engine.AddMessage(f"The {entity.name} dodged your attack!")
            else:
                # self.engine.PlaySound(f"hit_{random.randint(1, 3)}")

                if not self.melee_weapon:
                    dmg = self.stats[PlayerStats.STRENGTH] - 1
                else:
                    dmg = self.melee_weapon.roll_damage(self.stats[PlayerStats.STRENGTH])

                self.engine.AddMessage(f"You deal {dmg} damage to the {entity.name}!")

                entity.hp -= dmg

                if entity.hp <= 0:
                    self.engine.AddMessage(f"You killed the {entity.name}!")

                    entity.Kill()
        else:
            self.engine.AddMessage(f"You missed the {entity.name}.")
                            
        self.engine.advance_time = True
        self.engine.action_time = action_times[Actions.MELEE_ATTACK]
    
    def AttackRanged(self, entity):
        if random.random() <= self.ChanceToHitRanged():
            # hit successful

            # self.engine.PlaySound(f"hit_{random.randint(1, 3)}")

            dmg = self.ranged_weapon.roll_damage()

            self.engine.AddMessage(f"You deal {dmg} damage to the {entity.name}!")

            entity.hp -= dmg

            if entity.hp <= 0:
                self.engine.AddMessage(f"You killed the {entity.name}!")

                entity.Kill()
        else:
            self.engine.AddMessage(f"You missed the {entity.name}.")

    def FireWeapon(self, x, y):
        # check for line of fire between self and point
        sx = self.x
        sy = self.y
        a = math.atan2(y - sy, x - sx)

        self.firing = True
        self.heading = a
        self.projx, self.projy = sx, sy