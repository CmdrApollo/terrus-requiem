from item import *
from utils import *
import math

class Player:
    def __init__(self, engine, x, y):
        self.engine = engine

        self.x = x
        self.y = y

        self.endurance = 5
        self.dexterity = 5
        self.intelligence = 5
        self.perception = 5
        self.strength = 5

        self.sight_distance = 5 + self.perception

        self.melee_weapon = Club()
        self.ranged_weapon = BasicBlaster()
        self.armor = LightArmor()

        self.speed = 100

        self.health = self.max_health = 100

        self.energy = self.max_energy = 100

        self.firing = False
        self.heading = 0
        self.projx = 0
        self.projy = 0

        self.inventory = []

        self.capacity = 20

    def CanPickupItem(self):
        return len(self.inventory) < self.capacity

    def GiveItem(self, item):
        self.inventory.append(item)

    def AttemptToDamage(self, name, dmg):
        d = dmg
        if random.randint(1, 10) <= self.dexterity - 1:
            self.engine.AddMessage(f"You dodged the attack from the {name}!")
            return
        if self.armor:
            d = self.armor.FilterDamage(d)
        if d == 0:
            self.engine.AddMessage(f"Your armor protected you from the {name}!")
        else:
            self.health = max(0, self.health - d)
            self.engine.AddMessage(f"The {name} hit you for {d} damage!")
            if self.armor:
                self.engine.AddMessage(f"Your armor ablated!")
                if self.armor.destroyed:
                    self.engine.AddMessage(f"Your armor was destroyed!")
            if self.health == 0:
                self.engine.AddMessage(f"You died!")

                # TODO write this function...
                self.engine.OnGameOver()

    def ChanceToHitMelee(self):
        return + ((self.perception + 1) / 10)

    def ChanceToHitRanged(self):
        return + ((self.perception + 1) / 10)
    
    def AttackMelee(self, entity):
        if random.random() <= self.ChanceToHitMelee():
            # hit successful
            
            if random.random() <= entity.chance_to_dodge:
                # enemy dogdged

                self.engine.AddMessage(f"The {entity.name} dodged your attack!")
            else:
                self.engine.PlaySound(f"hit_{random.randint(1, 3)}")

                dmg = self.melee_weapon.roll_damage(self.strength)

                self.engine.AddMessage(f"You deal {dmg} damage to the {entity.name}!")

                entity.hp -= dmg

                if entity.hp <= 0:
                    self.engine.AddMessage(f"You killed the {entity.name}!")

                    entity.Kill()
        else:
            self.engine.AddMessage(f"You missed the {entity.name}.")
                            
        self.engine.advance_time = True
        self.engine.action_time = action_times[Actions.RANGED_ATTACK]
    
    def AttackRanged(self, entity):
        if random.random() <= self.ChanceToHitRanged():
            # hit successful

            self.engine.PlaySound(f"hit_{random.randint(1, 3)}")

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