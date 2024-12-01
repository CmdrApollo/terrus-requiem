from pyne.pyne import *
from perlin_noise import PerlinNoise
from area_map import *
from names import *
from utils import *
import random

class ColorScheme:
    def __init__(self, forest, hills, plains, beaches, water, deep_water):
        self.forest = forest
        self.hills = hills
        self.plains = plains
        self.beaches = beaches
        self.water = water
        self.deep_water = deep_water

schemes = {
    'earth-like': ColorScheme(
        PyneEngine.Color.DARK_GREEN,
        PyneEngine.Color.BROWN,
        PyneEngine.Color.LIGHT_GREEN,
        PyneEngine.Color.LIGHT_YELLOW,
        PyneEngine.Color.CYAN,
        PyneEngine.Color.DARK_CYAN
    ),
    'mars-like': ColorScheme(
        PyneEngine.Color.RED,
        PyneEngine.Color.BROWN,
        PyneEngine.Color.LIGHT_RED,
        PyneEngine.Color.ORANGE,
        PyneEngine.Color.YELLOW,
        PyneEngine.Color.DARK_YELLOW
    ),
    'ice-world': ColorScheme(
        PyneEngine.Color.BLUE,
        PyneEngine.Color.WHITE,
        PyneEngine.Color.LIGHT_BLUE,
        PyneEngine.Color.WHITE,
        PyneEngine.Color.CYAN,
        PyneEngine.Color.DARK_CYAN
    )
}

class Planet:
    def __init__(self, name, engine, scheme=None, seed=None, hand_placed_areas=False):
        self.name = name
        self.engine = engine

        self.player_start_x = terminal_width // 2
        self.player_start_y = terminal_height // 2

        self.overworld = engine.Buffer(self.engine.TerminalWidth(), self.engine.TerminalHeight() - 5)

        self.areas = []
        
        self.seed = string_to_seed(self.name) if not seed else seed

        self.contains_base = False

        self.noise = PerlinNoise(1.5, self.seed)
        self.fine_noise = PerlinNoise(3, self.seed + 1)

        random.seed(self.seed)

        _scheme = scheme if scheme else random.choice(list(schemes.keys()))

        self.color_scheme = schemes[_scheme]

        for x in range(self.overworld.width):
            for y in range(self.overworld.height):
                cn = self.noise.noise((x / self.overworld.width, y / self.overworld.height))
                fn = self.fine_noise.noise((x / self.overworld.width, y / self.overworld.height)) / 2
                
                n = cn + fn
                if n > 0.0:
                    char = "\""
                    color = self.color_scheme.plains
                elif n > -0.05:
                    char = '+'
                    color = self.color_scheme.beaches
                elif n > -0.125:
                    char = "="
                    color = self.color_scheme.water
                else:
                    char = "="
                    color = self.color_scheme.deep_water

                if char != "=":
                    if n > 0.25 and fn < 0.0:
                        char = "~"
                        color = self.color_scheme.hills
                    elif fn > 0.05:
                        char = "&"
                        color = self.color_scheme.forest

                    if not hand_placed_areas:
                        random_location = random.randint(0, 1000)

                        if random_location == 0:
                            # Spawn a Shipwreck.
                            char = 'x'
                            color = PyneEngine.Color.GRAY

                            self.areas.append(Shipwreck(f"Shipwreck of the {generate_ship_name()}", self, self.engine, x, y))
                        elif random_location < 3:
                            char = '*'
                            # Keep the color that has already been decided

                            self.areas.append(Cave(generate_cave_name(), self, self.engine, x, y))
                        elif random_location < 9:
                            char = 'o'
                            # Keep the color that has already been decided

                            self.areas.append(Settlement(generate_settlement_name(), self, self.engine, x, y))

                engine.DrawChar(char, (color, engine.Color.BACKGROUND), x, y, self.overworld)

class PlanetXAB112(Planet):
    def __init__(self, engine):
        super().__init__('XA-B1-12', engine, 'earth-like', 4, hand_placed_areas=True)

        engine.DrawChar('x', (PyneEngine.Color.GRAY, engine.Color.BACKGROUND), 13, 15, self.overworld)
        self.areas.append(Shipwreck(f"Shipwreck of the {generate_ship_name()}", self, self.engine, 13, 15))

        engine.DrawChar('o', (PyneEngine.Color.DARK_GREEN, engine.Color.BACKGROUND), 27, 12, self.overworld)
        self.areas.append(Yoore(self, self.engine, 27, 12))