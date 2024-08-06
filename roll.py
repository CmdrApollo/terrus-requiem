import random

class Roll:
    def __init__(self, x, y, z):
        # Roll is xDy + z
        # e.g. 1D4 + 6
        
        self.x, self.y, self.z = x, y, z
    
    def roll(self):
        return sum([random.randint(1, self.y) for _ in range(self.x)]) + self.z