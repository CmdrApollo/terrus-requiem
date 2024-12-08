from pyne.pyne import PyneEngine
from roll import *

class ItemClass:
    MELEE_WEAPON = 0
    RANGED_WEAPON = 1

    ARMOR = 2

class MeleeWeaponType:
    BLUNT = 0
    SHARP = 1

class Item:
    def __init__(self, name: str, item_class: int, char: str, color: str):
        self.name = name
        self.item_class = item_class
        self.char = char
        self.color = color
    
class MeleeWeapon(Item):
    def __init__(self, name: str, weapon_type: int, roll: Roll, char: str, color: str):
        super().__init__(name, ItemClass.MELEE_WEAPON, char, color)

        self.weapon_type = weapon_type
        self.roll = roll
    
    def roll_damage(self, external_modifier=0):
        return self.roll.roll() + external_modifier
    
class Club(MeleeWeapon):
    def __init__(self):
        super().__init__("Club", ItemClass.MELEE_WEAPON, Roll(2, 4, 2), '*', PyneEngine.Color.BROWN) # 2d4+2

class RangedWeapon(Item):
    def __init__(self, name: str, proj_char: str, proj_color: str, weapon_type: int, roll: Roll, char: str, color: str):
        super().__init__(name, ItemClass.RANGED_WEAPON, char, color)

        self.weapon_type = weapon_type
        self.roll = roll
        self.proj_char = proj_char
        self.proj_color = proj_color
    
    def roll_damage(self, external_modifier=0):
        return self.roll.roll() + external_modifier

class Blaster(RangedWeapon):
    def __init__(self):
        super().__init__("Blaster", '/', PyneEngine.Color.RED, ItemClass.RANGED_WEAPON, Roll(2, 6, 2), '*', PyneEngine.Color.GRAY) # 1d6+2

class Armor(Item):
    def __init__(self, name: str, pv: int, char: str, color: str):
        super().__init__(name, ItemClass.ARMOR, char, color)
        self.pv = pv

class LightArmor(Armor):
    def __init__(self):
        super().__init__("Light Armor", 6, '%', PyneEngine.Color.GRAY)