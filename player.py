from item import *

class Player:
    def __init__(self, engine, x, y):
        self.engine = engine

        self.x = x
        self.y = y

        self.credits = 1000

        self.homeworld = None
        self.character_class = None

        self.endurance = 5
        self.dexterity = 5
        self.intelligence = 5
        self.perception = 5
        self.strength = 5

        self.sight_distance = 5 + self.perception

        self.melee_weapon = Club()
        self.ranged_weapon = None
        self.armor = None

        self.speed = 100

        self.health = self.max_health = 100

    def AttemptToDamage(self, name, dmg):
        d = dmg
        if random.randint(1, 10) <= self.dexterity:
            self.engine.AddMessage(f"You dodged the attack from the {name}!")
            return
        self.health = max(0, self.health - d)
        self.engine.AddMessage(f"The {name} hit you for {d} damage!")
        if self.health == 0:
            self.engine.AddMessage(f"You died!")

            # TODO write this function...
            self.engine.OnGameOver()

    def ChanceToHitMelee(self):
        return + (self.perception / 10)
    
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