from pyne.pyne import PyneEngine
from .roll import *

class ItemClass:
    MELEE_WEAPON = 0
    RANGED_WEAPON = 1

    ARMOR = 2

    CORPSE = 3

    MISC = 4

class MeleeWeaponType:
    BLUNT = 0
    SHARP = 1

class Item:
    def __init__(self, name: str, item_class: int, char: str, color: str):
        self.name = name
        self.item_class = item_class
        self.char = char
        self.color = color
        
        self.destroyed = False
    
class MeleeWeapon(Item):
    def __init__(self, name: str, weapon_type: int, roll: Roll, char: str, color: str):
        super().__init__(name, ItemClass.MELEE_WEAPON, char, color)

        self.weapon_type = weapon_type
        self.roll = roll
    
    def roll_damage(self, external_modifier=0):
        return self.roll.roll() + external_modifier

class Rock(MeleeWeapon):
    def __init__(self):
        super().__init__("Rock", MeleeWeaponType.BLUNT, Roll(1, 4, 2), 'o', PyneEngine.Color.GRAY) # 1d4+2 blunt
    
class Club(MeleeWeapon):
    def __init__(self):
        super().__init__("Club", MeleeWeaponType.BLUNT, Roll(2, 4, 2), '/', PyneEngine.Color.BROWN) # 2d4+2 blunt
    
class BasicSpear(MeleeWeapon):
    def __init__(self):
        super().__init__("Bsc. Spear", MeleeWeaponType.SHARP, Roll(1, 6, 4), '/', PyneEngine.Color.GRAY) # 1d6+4 sharp
    
class AdvancedSpear(MeleeWeapon):
    def __init__(self):
        super().__init__("Adv. Spear", MeleeWeaponType.SHARP, Roll(2, 6, 4), '/', PyneEngine.Color.WHITE) # 1d6+4 sharp

class RangedWeapon(Item):
    def __init__(self, name: str, proj_char: str, proj_color: str, weapon_type: int, roll: Roll, max_shot_distance: int, char: str, color: str):
        super().__init__(name, ItemClass.RANGED_WEAPON, char, color)

        self.weapon_type = weapon_type
        self.roll = roll
        self.max_shot_distance = max_shot_distance
        self.proj_char = proj_char
        self.proj_color = proj_color
    
    def roll_damage(self, external_modifier=0):
        return self.roll.roll() + external_modifier

class BasicBlaster(RangedWeapon):
    def __init__(self):
        super().__init__("Bsc. Blaster", '/', PyneEngine.Color.YELLOW, ItemClass.RANGED_WEAPON, Roll(1, 6, 2), 10, '[', PyneEngine.Color.GRAY) # 1d6+2

class AdvancedBlaster(RangedWeapon):
    def __init__(self):
        super().__init__("Adv. Blaster", '/', PyneEngine.Color.RED, ItemClass.RANGED_WEAPON, Roll(2, 6, 2), 15, '[', PyneEngine.Color.WHITE) # 2d6+2

class Armor(Item):
    def __init__(self, name: str, pv: int, char: str, color: str):
        super().__init__(name, ItemClass.ARMOR, char, color)
        self.pv = pv
    
    def FilterDamage(self, d):
        dmg = max(0, d - self.pv)
        if dmg:
            self.pv -= 1

            if self.pv <= 0:
                self.pv = 0
                self.destroyed = True
        return dmg

class LightArmor(Armor):
    def __init__(self):
        super().__init__("Light Armor", 6, '%', PyneEngine.Color.BROWN)

class MediumArmor(Armor):
    def __init__(self):
        super().__init__("Medium Armor", 8, '%', PyneEngine.Color.GRAY)

class HeavyArmor(Armor):
    def __init__(self):
        super().__init__("Heavy Armor", 10, '%', PyneEngine.Color.WHITE)

class Corpse(Item):
    def __init__(self, name, color):
        super().__init__(name, ItemClass.CORPSE, '%', color)

class RatCorpse(Corpse):
    def __init__(self):
        super().__init__("Rat Corpse", PyneEngine.Color.BROWN)