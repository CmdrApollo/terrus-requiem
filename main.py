from pyne.pyne import *
from planet import Planet
from entity import *
from area_map import *
from ship_chassis import *
from utils import *

import numpy as np
import tcod.map
import tcod.constants

GAME_NAME = "Terrus Requiem"
GAME_VERSION = "v0.0.1"

main_menu = PyneEngine.Buffer(terminal_width, terminal_height)

# If we move onto a tile that is non-descriptive, give the generic terrain description
overworld_tile_descriptions = {
    '&': 'A Forest.',
    '"': 'Plains.',
    '=': 'A Body of Water.',
    '^': 'Mountains.',
    '.': 'A Road.',
    '~': 'Hills.',
    '+': 'Beaches.',

    'b': 'Your Base.',

    'x': 'A Shipwreck.',
    '*': 'A Cave Entrance.',
    'o': 'A Settlement.'
}

terrain_symbols = ['"', '+', '&', '~']

DEBUG = True

class GameScene:
    MAIN_MENU = 0

    PLANET_OVERWORLD = 1
    PLANET_AREA = 2
    
    PLAYER_BASE = 3

    DUNGEON = 4
    CAVE = 5

    OUTER_SPACE = 6

    INVENTORY = 7
    PLAYER_STATS = 8

    BASE_INFO = 9

class Actions:
    CLOSE_DOOR = 0

class Game(PyneEngine):
    TITLE = "Terrus Requiem"

    def __init__(self, terminal_width=terminal_width, terminal_height=terminal_height, target_size=(1600, 900)):
        super().__init__(terminal_width, terminal_height, target_size)

        self.ship_chassis = {
            'Z800': generate_chassis_Z800(self),
            'X40': generate_chassis_X40(self)
        }

        self.game_window = self.Buffer(self.TerminalWidth(), self.TerminalHeight() - 5)
    
        self.current_planet = Planet("XA-B1-12", self, seed = 4)

        self.player = Player(self, self.game_window.width // 2, self.game_window.height // 2)

        self.current_scene = GameScene.MAIN_MENU

        self.current_map = None

        self.current_overlapping_element = None

        self.messages = []

        self.waiting_for_wall_place = False

        self.renaming_base = False

        self.user_text_input = ""

        self.first_frame = True

        self.advance_time = False

        self.waiting_for_direction = False

        self.waiting_action = None

    def AddMessage(self, message):
        self.messages.append(message)

    def OnConstruct(self):
        self.Clear(' ', (self.Color.WHITE, self.Color.BLACK), main_menu)

        self.DrawRect((self.Color.CYAN, self.Color.BLACK), 0, 0, self.TerminalWidth() - 1, self.TerminalHeight() - 1, scr=main_menu)
        
        self.DrawTextLines(t := [
            r"  />  ___   ___   ___   ___         ___  <\  ",
            r" //  | | | |   | |   | |   | |   | |   |  \\ ",
            r"<<     |   |__   |___| |___| |   | |___    >>",
            r" \\    |   |     |  \  |  \  |   |     |  // ",
            r"  \>   |   |___| |   | |   |  \_/| |___| </  ",
            r"                                             ",
            r"-[=]-[=]-[=]-[=]-[=]-[=]-[=]-[=]-[=]-[=]-[=]-",
            r"   ___   ___    _          ___   ___   ___   ",
            r"  |   | |   |  / \  |   | | | | |   | | | |  ",
            r"  |___| |__   |   | |   |   |   |__   | | |  ",
            r"  |  \  |     |  \| |   |   |   |     |   |  ",
            r"  |   | |___|  \_/\  \_/| |_|_| |___| |   |  ",
        ], (self.Color.WHITE, self.Color.BLACK), x := (self.TerminalWidth() // 2 - len(t[0]) // 2), y := 2, scr = main_menu)

        for i in [0, 1, 2, 3, 41, 42, 43, 44]:
            for j in range(5):
                self.SetColor((self.Color.YELLOW, self.Color.BLACK), x + i, y + j, main_menu)
            
        # for i in range(45):
        #     self.SetColor((self.Color.DARK_MAGENTA if not (i % 4) else self.Color.DARK_RED, self.Color.BLACK), x + i, y + 6, scr = main_menu)

        self.DrawTextLines(lines := [
            "p - Play             ",
            "l - Load Game        ",
            "x - Delete Saved Game",
            "c - Credits          ",
            "q - Quit             ",
        ], (self.Color.YELLOW, self.Color.BLACK), x := self.TerminalWidth() // 2 - len(lines[0]) // 2, y := self.TerminalHeight() - len(lines) - 3, scr = main_menu)

        for i in range(3):
            for j in range(5):
                self.SetColor((self.Color.WHITE, self.Color.BLACK), x + i, y + j, scr = main_menu)

        self.DrawTextLines([GAME_VERSION], (self.Color.WHITE, self.Color.BLACK), self.TerminalWidth() - 2, self.TerminalHeight() - 2, True, scr = main_menu)

        return True
    
    def GenerateSolidsMap(self):
        solids = np.array([[ 0 for _ in range(self.current_map.width) ] for _ in range(self.current_map.height)])
        solids[:] = True

        for x in range(self.current_map.width):
            for y in range(self.current_map.height):
                if self.current_map.data.GetAt(x, y).symbol == '#' or any([e.solid and e.x == x and e.y == y for e in self.current_map.entities]):
                    solids[y, x] = False
        
        self.solids = solids

    def HandleTextInput(self):
        if self.HasTextCache():
            self.user_text_input += self.TextCache()
        elif self.KeyPressed(K_BACKSPACE):
            self.user_text_input = self.user_text_input[:-1]

    def HandleMoveAndInteract(self):
        # returns which entity we attempt to move into

        attempt_move = False

        attempt_move_x = 0
        attempt_move_y = 0
        
        if self.KeyPressed(K_UP) or self.KeyPressed(K_KP8):
            attempt_move = True
            attempt_move_x = self.player.x + 0
            attempt_move_y = self.player.y - 1
        if self.KeyPressed(K_DOWN) or self.KeyPressed(K_KP2):
            attempt_move = True
            attempt_move_x = self.player.x + 0
            attempt_move_y = self.player.y + 1
        if self.KeyPressed(K_LEFT) or self.KeyPressed(K_KP4):
            attempt_move = True
            attempt_move_x = self.player.x - 1
            attempt_move_y = self.player.y + 0
        if self.KeyPressed(K_RIGHT) or self.KeyPressed(K_KP6):
            attempt_move = True
            attempt_move_x = self.player.x + 1
            attempt_move_y = self.player.y + 0
        if self.KeyPressed(K_KP9):
            attempt_move = True
            attempt_move_x = self.player.x + 1
            attempt_move_y = self.player.y - 1
        if self.KeyPressed(K_KP3):
            attempt_move = True
            attempt_move_x = self.player.x + 1
            attempt_move_y = self.player.y + 1
        if self.KeyPressed(K_KP1):
            attempt_move = True
            attempt_move_x = self.player.x - 1
            attempt_move_y = self.player.y + 1
        if self.KeyPressed(K_KP7):
            attempt_move = True
            attempt_move_x = self.player.x - 1
            attempt_move_y = self.player.y - 1

        if attempt_move:
            allow_move = True

            scr_el = self.game_window.GetAt(attempt_move_x, attempt_move_y)

            if not scr_el:
                # player is attempting to move to an out of bounds position
                return
            
            match scr_el.symbol:
                # check what character we are about to collide with
                case '#' | '=':
                    # if it is wall or water, abort the movement
                    allow_move = False
                case _:
                    # otherwise we chill
                    
                    if self.current_map:
                        for e in self.current_map.entities:
                            if e.x == attempt_move_x and e.y == attempt_move_y:
                                return e

            if allow_move:
                self.player.x = attempt_move_x
                self.player.y = attempt_move_y

                self.advance_time = True
        
        return None
    
    def AdvanceTime(self):
        for e in self.current_map.entities:
            e.OnMyTurn(self)
        
        # self.GenerateSolidsMap()

        self.advance_time = False

    def LoadMap(self, area, is_base=False):
        self.current_map = area
        self.current_scene = GameScene.PLANET_AREA if not is_base else GameScene.PLAYER_BASE
        
        self.player.x = self.TerminalWidth() // 2
        self.player.y = self.TerminalHeight() // 2

    def LoadOverworld(self):
        self.player.x = self.current_map.x
        self.player.y = self.current_map.y

        self.current_scene = GameScene.PLANET_OVERWORLD

    def HandleDirection(self):
        if self.waiting_for_direction:
            self.waiting_for_direction = False

            if self.KeyPressed(K_KP8):        self.direction_x, self.direction_y = + 0, - 1
            elif self.KeyPressed(K_KP9):      self.direction_x, self.direction_y = + 1, - 1
            elif self.KeyPressed(K_KP6):      self.direction_x, self.direction_y = + 1, + 0
            elif self.KeyPressed(K_KP3): self.direction_x, self.direction_y = + 1, + 1
            elif self.KeyPressed(K_KP2):  self.direction_x, self.direction_y = + 0, + 1
            elif self.KeyPressed(K_KP1):      self.direction_x, self.direction_y = - 1, + 1
            elif self.KeyPressed(K_KP4):      self.direction_x, self.direction_y = - 1, + 0
            elif self.KeyPressed(K_KP7):      self.direction_x, self.direction_y = - 1, - 1
            else: self.waiting_for_direction = True

            return not self.waiting_for_direction

        return False

    def OnUpdate(self, delta):
        if self.first_frame:
            # if we don't do this and the user hits a key to skip the engine intro,
            # the first line of text gets skipped entirely
            self.first_frame = False
            return True

        self.current_overlapping_element = self.current_planet.overworld.GetAt(self.player.x, self.player.y)

        if self.current_scene not in [GameScene.MAIN_MENU, GameScene.INVENTORY, GameScene.BASE_INFO]:
            if len(self.messages):
                # If we pressed any key (basically), remove the first message in the queue

                if self.HasTextCache() or any([self.KeyPressed(x) for x in [K_UP, K_DOWN, K_LEFT, K_RIGHT, K_KP1, K_KP2, K_KP3, K_KP4, K_KP6, K_KP7, K_KP8, K_KP9]]):
                    self.messages.pop(0)
                
                # Quit-out early. this is a choke point for the program
                # the user cannot do anything until they drain the message queue
                
                if len(self.messages) > 0:
                    return True

        cache = self.TextCache() if self.HasTextCache() else None
        
        match self.current_scene:
            case GameScene.MAIN_MENU:
                if cache == 'p':
                    # TODO : switch this to character creation
                    self.current_scene = GameScene.PLANET_OVERWORLD
                elif cache == 'q':
                    return False

            case GameScene.PLANET_OVERWORLD:
                self.HandleMoveAndInteract()

                if cache == 'b':
                    if self.current_overlapping_element.symbol in terrain_symbols:
                        if not self.current_planet.contains_base:
                            # If the player presses 'b' and the current planet does not currently have a base, create one.
                            self.DrawChar(
                                'b',
                                (self.current_overlapping_element.fg, self.Color.BLACK),
                                self.player.x, self.player.y,
                                self.current_planet.overworld
                            )

                            self.current_planet.contains_base = True

                            self.current_planet.areas.append(Base(f"{self.current_planet.name} Base", self.current_planet, self, self.player.x, self.player.y))
                        else:
                            self.AddMessage("You already have a base on this planet!")
                    else:
                        self.AddMessage("You can't place your base here!")
                elif cache == '>':
                    # player is attempting to enter an area
                    
                    for area in self.current_planet.areas:
                        if area.x == self.player.x and area.y == self.player.y:
                            self.LoadMap(area, self.current_overlapping_element.symbol == 'b')

                            self.AddMessage(f"You entered '{self.current_map.name}'.")

                            self.GenerateSolidsMap()

                            break

            case GameScene.PLANET_AREA:
                if not self.waiting_for_direction:
                    move_interact_entity = self.HandleMoveAndInteract()
                else:
                    move_interact_entity = None


                has_direction = self.HandleDirection()

                if has_direction:
                    match self.waiting_action:
                        case Actions.CLOSE_DOOR:
                            for e in self.current_map.entities:
                                if e.x == self.player.x + self.direction_x and e.y == self.player.y + self.direction_y:
                                    if type(e) in [Door, Hatch]:
                                        if e.solid:
                                            self.AddMessage(f"{'Door' if type(e) == Door else 'Hatch'} is already closed.")
                                        else:
                                            self.AddMessage(f"You close the {'door' if type(e) == Door else 'hatch'}.")

                                            e.Close()

                                            self.advance_time = True

                                            self.GenerateSolidsMap()
                                    else:
                                        self.AddMessage("You can't close that!")

                    self.waiting_action = None
                    self.waiting_for_direction = False

                if cache == 'c':
                    self.waiting_for_direction = True
                    self.waiting_action = Actions.CLOSE_DOOR
                    self.AddMessage("Close door in what direction?")

                if move_interact_entity:
                    self.advance_time = True

                    move_interact_entity.PlayerMoveInteract(self, self.player)
                    
                    if move_interact_entity.to_remove:
                        self.current_map.entities.remove(move_interact_entity)

                    if type(move_interact_entity) in [Door, Hatch]:
                        # If we open a door, regenerate the solids map
                        self.GenerateSolidsMap()
                
                if self.advance_time:
                    self.AdvanceTime()
            
            case GameScene.PLAYER_BASE:
                self.HandleMoveAndInteract()

                if cache == '<':
                    self.AddMessage("You leave your base.")
                    self.LoadOverworld()
                elif cache == 'b':
                    self.current_scene = GameScene.BASE_INFO
                
                if cache != 'c':
                    self.waiting_for_wall_place = False

            case GameScene.DUNGEON:
                self.HandleMoveAndInteract()
            
            case GameScene.CAVE:
                self.HandleMoveAndInteract()
            
            case GameScene.OUTER_SPACE:
                pass
            
            case GameScene.INVENTORY:
                pass
            
            case GameScene.PLAYER_STATS:
                pass

            case GameScene.BASE_INFO:
                if self.renaming_base:
                    self.HandleTextInput()
                    
                    if self.KeyPressed(K_RETURN):

                        self.renaming_base = False
                        self.current_map.name = self.user_text_input

                        self.user_text_input = ''
                else:
                    if cache == 'z':
                        # exit menu
                        self.current_scene = GameScene.PLAYER_BASE
                    elif cache == 'n':
                        self.renaming_base = True
        
        return True
    
    def DrawEntities(self):
        for e in self.current_map.entities:
            self.DrawChar(e.repr.symbol, (e.repr.fg, e.repr.bg), e.x, e.y, self.game_window)

    def OnDraw(self):
        self.Clear(' ', (self.Color.WHITE, self.Color.BLACK))
        self.Clear(' ', (self.Color.WHITE, self.Color.BLACK), self.game_window)

        # self.DrawRect((self.Color.WHITE, self.Color.BLACK), 0, 2, self.TerminalWidth() - 1, self.TerminalHeight() - 6)
        
        match self.current_scene:
            case GameScene.MAIN_MENU:
                
                self.BlitBuffer(main_menu, 0, 0)
                return True

            case GameScene.PLANET_OVERWORLD:
                self.BlitBuffer(self.current_planet.overworld, 0, 0, self.game_window)
                self.DrawText(f"{self.current_planet.name} Overworld", (self.Color.WHITE, self.Color.BLACK), 0, self.TerminalHeight() - 1)

            case GameScene.PLANET_AREA:
                self.BlitBuffer(self.current_map.data, 0, 0, self.game_window)
                self.DrawText(self.current_map.name, (self.Color.WHITE, self.Color.BLACK), 0, self.TerminalHeight() - 1)
            
                self.DrawEntities()

            case GameScene.PLAYER_BASE:
                self.BlitBuffer(self.current_map.data, 0, 0, self.game_window)
                self.DrawText(self.current_map.name, (self.Color.WHITE, self.Color.BLACK), 0, self.TerminalHeight() - 1)

            case GameScene.DUNGEON:
                pass
            
            case GameScene.CAVE:
                pass
            
            case GameScene.OUTER_SPACE:
                pass
            
            case GameScene.INVENTORY:
                pass
            
            case GameScene.PLAYER_STATS:
                pass

            case GameScene.BASE_INFO:
                self.Clear(' ', (self.Color.WHITE, self.Color.BLACK), self.game_window)
                self.DrawTextLines(
                    [
                        "Base Info",
                        "-"*self.game_window.width,
                    ],
                    (self.Color.YELLOW, self.Color.BLACK), 0, 0,
                    scr = self.game_window
                )
                self.DrawTextLines(
                    [
                        f'Name   -',
                        f'Planet -',
                        '',
                        f'Level  -',
                        f'EXP    -',
                    ],
                    (self.Color.WHITE, self.Color.BLACK), 0, 3,
                    scr = self.game_window
                )
                self.DrawTextLines(
                    [
                        f'{self.current_map.name}',
                        f'{self.current_planet.name}',
                        '',
                        f'{self.current_map.level}',
                        f'{self.current_map.exp}/{self.current_map.exp_to_level_up}'
                    ],
                    (self.Color.YELLOW, self.Color.BLACK), 10, 3,
                    scr = self.game_window
                )

                if self.renaming_base:
                    self.FillRect(' ', (0, 0), self.game_window.width // 2 - 20, self.game_window.height // 2 - 4, 40, 8, scr = self.game_window)
                    self.DrawRect((self.Color.WHITE, self.Color.BLACK), self.game_window.width // 2 - 20, self.game_window.height // 2 - 4, 40, 8, scr = self.game_window)

                    self.DrawTextLines(["Rename your base to what?", '-' * 39], (self.Color.YELLOW, self.Color.BLACK), self.game_window.width // 2 - 19, self.game_window.height // 2 - 3, scr=self.game_window)

                    self.DrawText(self.user_text_input + '_', (self.Color.WHITE, self.Color.BLACK), self.game_window.width // 2 - 19, self.game_window.height // 2 - 1, scr = self.game_window)

                self.DrawText(t := "n - Rename Base     z - Exit", (self.Color.WHITE, self.Color.BLACK), self.TerminalWidth() - (len(t) + 1), self.TerminalHeight() - 1)

        if self.current_scene != GameScene.BASE_INFO:
            self.DrawChar('@', (self.Color.LIGHT_MAGENTA, self.Color.BLACK), self.player.x, self.player.y, self.game_window)

        if self.current_map:
            fov = tcod.map.compute_fov(self.solids, (self.player.y, self.player.x), 3 * self.player.sight_distance, algorithm=tcod.constants.FOV_DIAMOND)

            if self.current_map:
                active_visibility: list[bool] = self.current_map.visibility.copy()
                active_visibility = [False for _ in range(len(active_visibility))]

            for x in range(self.game_window.width):
                for y in range(self.game_window.height):
                    if fov[y, x] and self.current_map:
                        self.current_map.visibility[y * self.current_map.width + x] = True
                        active_visibility[y * self.current_map.width + x] = True
                    
                    if self.current_map and not self.current_map.visibility[y * self.current_map.width + x]:
                        self.DrawChar('?', (self.Color.VERY_DARK_GRAY, self.Color.BLACK), x, y, self.game_window)
                    
                    if self.current_map and self.current_map.visibility[y * self.current_map.width + x] and not active_visibility[y * self.current_map.width + x]:
                        e = self.game_window.GetAt(x, y)
                        self.DrawChar(e.symbol, (self.DarkenColor(e.fg), self.DarkenColor(e.bg)), x, y, self.game_window)

        self.BlitBuffer(self.game_window, 0, 2)

        if len(self.messages):
            # If we have messages, display the first one
            msg = self.messages[0] + (' (more)' if len(self.messages) != 1 else '')

            if len(msg) > self.TerminalWidth() - 1:
                lines = ['']
                size = 0

                for el in msg.split(' '):
                    lines[-1] += el + ' '

                    size += len(el) + 1

                    if size > self.TerminalWidth() - 5:
                        lines.append('')
                        size = 0
                
                # if len(lines) > 2:
                #     self.AddMessage(' '.join(lines[2:]))
            else:
                lines = [msg]

            self.DrawTextLines(lines[:2], (self.Color.WHITE, self.Color.BLACK), 0, 0)
        elif self.current_scene == GameScene.PLANET_OVERWORLD:
            # Otherwise, attempt to show the generic description of the tile we are on
            if self.current_overlapping_element.symbol in overworld_tile_descriptions:
                self.DrawText(overworld_tile_descriptions[self.current_overlapping_element.symbol], (self.Color.WHITE, self.Color.BLACK), 0, 0)

        if DEBUG:
            mx, my = self.MousePos()

            self.SetColor((self._scr_buf.GetAt(mx, my).fg, self.Color.WHITE), mx, my)
            self.DrawTextLines([f"{mx, my}"], (self.Color.WHITE, self.Color.BLACK), self.TerminalWidth() - 1, 0, True)

        return True

game = Game(terminal_width, terminal_height)
game.start()