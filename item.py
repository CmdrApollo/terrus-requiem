from roll import *

class ItemClass:
    MELEE_WEAPON = 0
    RANGED_WEAPON = 1

    ARMOR_HEAD = 2
    ARMOR_BODY = 3
    ARMOR_ARMS = 4
    ARMOR_LEGS = 5

class MeleeWeaponType:
    BLUNT = 0
    SHARP = 1

class Item:
    def __init__(self, name: str, item_class: int):
        self.name = name
        self.item_class = item_class
    
class MeleeWeapon(Item):
    def __init__(self, name: str, weapon_type: int, roll: Roll):
        super().__init__(name, ItemClass.MELEE_WEAPON)

        self.weapon_type = weapon_type
        self.roll = roll
    
    def roll_damage(self):
        return self.roll.roll()

class RangedWeapon(Item):
    def __init__(self, name: str, weapon_type: int, roll: Roll):
        super().__init__(name, ItemClass.RANGED_WEAPON)

        self.weapon_type = weapon_type
        self.roll = roll
    
    def roll_damage(self):
        return self.roll.roll()