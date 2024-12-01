class CharacterClass:
    def __init__(self, name, traits, skills, attributes):
        self.name = name
        self.traits = traits
        self.skills = skills
        self.attributes = attributes

class Noble(CharacterClass):
    def __init__(self):
        super().__init__("Noble", [], {}, {})

class Scoundrel(CharacterClass):
    def __init__(self):
        super().__init__("Scoundrel", [], {}, {})

class Merchant(CharacterClass):
    def __init__(self):
        super().__init__("Merchant", [], {}, {})

class Mechanic(CharacterClass):
    def __init__(self):
        super().__init__("Mechanic", [], {}, {})