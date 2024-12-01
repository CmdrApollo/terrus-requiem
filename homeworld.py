class Homeworld:
    def __init__(self, name, traits, skills, attributes):
        self.name = name
        self.traits = traits
        self.skills = skills
        self.attributes = attributes
    
class Ajaet(Homeworld):
    def __init__(self):
        super().__init__("Ajaet", [], {}, {"intelligence": 1, "endurance": -1})
    
class Mokra(Homeworld):
    def __init__(self):
        super().__init__("Mokra", ["trapfinder"], {}, {"perception": 1})
    
class Terrus(Homeworld):
    def __init__(self):
        super().__init__("Terrus", ["sturdy"], {}, {})
    
class Zandar(Homeworld):
    def __init__(self):
        super().__init__("Zandar", ["controlled breathing"], {}, {})
    
class Space(Homeworld):
    def __init__(self):
        super().__init__("Space", ["child of space"], {"electronics": 5}, {})