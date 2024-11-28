from pyne.pyne import *
from planet import Planet
from entity import *
from area_map import *
from ship_chassis import *
from utils import *
from dialogue import DialogueManager

import numpy as np
import tcod.map
import tcod.constants

GAME_NAME = "Terrus Requiem"
GAME_VERSION = "v0.0.1"

# these screens are static, so they are stored as buffers for simplicity.
main_menu = PyneEngine.Buffer(terminal_width, terminal_height)
credits_screen = PyneEngine.Buffer(terminal_width, terminal_height)

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
    # All of the 'scenes' found in the game

    MAIN_MENU = 0
    CREDITS = 1

    PLANET_OVERWORLD = 2
    PLANET_AREA = 3
    
    PLAYER_BASE = 4

    DUNGEON = 5
    CAVE = 6

    OUTER_SPACE = 7

    INVENTORY = 8
    PLAYER_STATS = 9

    BASE_INFO = 10

class Actions:
    # actions that require a direction
    CLOSE_DOOR = 0

action_times = [ 75 ]

class Game(PyneEngine):
    # name of the game and title of the window
    TITLE = GAME_NAME

    def __init__(self, terminal_width=terminal_width, terminal_height=terminal_height, target_size=(1600, 900)):
        super().__init__(terminal_width, terminal_height, target_size)

        # generate the ship chassis buffers
        self.ship_chassis = {
            'Z800': generate_chassis_Z800(self),
            'X40': generate_chassis_X40(self)
        }

        # where most things get rendered besides the 5 lines of text
        self.game_window = self.Buffer(self.TerminalWidth(), self.TerminalHeight() - 5)
    
        self.current_planet = Planet("XA-B1-12", self, seed = 4)
        self.player = Player(self, self.game_window.width // 2, self.game_window.height // 2)

        # used for the pseudo-state machine
        self.current_scene = GameScene.MAIN_MENU

        # used for collisions and things
        self.current_map = None
        self.current_overlapping_element = None

        # dialogue manager
        self.dialogue_manager = DialogueManager()

        # the two lines at the top of the screen
        self.messages = []

        self.renaming_base = False

        self.user_text_input = ""

        self.first_frame = True

        # flag for if the user has performed an action
        self.advance_time = False
        self.action_time = 0

        # if the program should wait for a direction and what action it's waiting for
        # TODO: currently only close door action
        self.waiting_for_direction = False
        self.waiting_action = None

    # add messages to the queue
    def AddMessage(self, message):
        self.messages.append(message)

    def OnConstruct(self):
        # generate the main menu buffer

        self.Clear(' ', (self.Color.WHITE, self.Color.BACKGROUND), main_menu)

        self.DrawRect((self.Color.CYAN, self.Color.BACKGROUND), 0, 0, self.TerminalWidth() - 1, self.TerminalHeight() - 1, scr=main_menu)
        
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
        ], (self.Color.WHITE, self.Color.BACKGROUND), x := (self.TerminalWidth() // 2 - len(t[0]) // 2), y := 2, scr = main_menu)

        for i in [0, 1, 2, 3, 41, 42, 43, 44]:
            for j in range(5):
                self.SetColor((self.Color.YELLOW, self.Color.BACKGROUND), x + i, y + j, main_menu)
            
        # for i in range(45):
        #     self.SetColor((self.Color.DARK_MAGENTA if not (i % 4) else self.Color.DARK_RED, self.Color.BACKGROUND), x + i, y + 6, scr = main_menu)

        self.DrawTextLines(lines := [
            "p - Play             ",
            "l - Load Game        ",
            "x - Delete Saved Game",
            "c - Credits          ",
            "q - Quit             ",
        ], (self.Color.YELLOW, self.Color.BACKGROUND), x := self.TerminalWidth() // 2 - len(lines[0]) // 2, y := self.TerminalHeight() - len(lines) - 3, scr = main_menu)

        for i in range(3):
            for j in range(5):
                self.SetColor((self.Color.WHITE, self.Color.BACKGROUND), x + i, y + j, scr = main_menu)

        self.DrawTextLines([GAME_VERSION], (self.Color.WHITE, self.Color.BACKGROUND), self.TerminalWidth() - 2, self.TerminalHeight() - 2, True, scr = main_menu)
        
        # generate the credits screen buffer

        self.Clear(' ', (self.Color.WHITE, self.Color.BACKGROUND), credits_screen)

        self.DrawRect((self.Color.MAGENTA, self.Color.BACKGROUND), 0, 0, self.TerminalWidth() - 1, self.TerminalHeight() - 1, scr=credits_screen)
        
        self.DrawTextLines(t := [
            r"  />  ___   ___   ___   __    ___   ___   ___  <\  ",
            r" //  |   | |   | |   | |  \  | | | | | | |   |  \\ ",
            r"<<   |     |___| |__   |   |   |     |   |___    >>",
            r" \\  |     |  \  |     |   |   |     |       |  // ",
            r"  \> |___| |   | |___| |___| |_|_|   |   |___| </  ",
        ], (self.Color.WHITE, self.Color.BACKGROUND), x := (self.TerminalWidth() // 2 - len(t[0]) // 2), y := 2, scr = credits_screen)

        for i in [0, 1, 2, 3, 47, 48, 49, 50]:
            for j in range(5):
                self.SetColor((self.Color.YELLOW, self.Color.BACKGROUND), x + i, y + j, credits_screen)

        self.DrawTextLines(lines := [
            "z - Return",
        ], (self.Color.YELLOW, self.Color.BACKGROUND), x := self.TerminalWidth() // 2 - len(lines[0]) // 2, y := self.TerminalHeight() - len(lines) - 3, scr = credits_screen)

        for i in range(3):
            self.SetColor((self.Color.WHITE, self.Color.BACKGROUND), x + i, y, scr = credits_screen)

        self.DrawChar('@', (self.Color.LIGHT_MAGENTA, self.Color.BACKGROUND), x := self.TerminalWidth() // 3, y := self.TerminalHeight() // 4 + 4, credits_screen)
        self.DrawText(t := "Mélanie J.", (self.Color.WHITE, self.Color.BACKGROUND), x - len(t) // 2, y + 1, credits_screen)
        self.DrawText(t := "<The Creator>", (self.Color.GRAY, self.Color.BACKGROUND), x - len(t) // 2, y + 2, credits_screen)

        self.DrawChar('@', (self.Color.LIGHT_BLUE, self.Color.BACKGROUND), x := (self.TerminalWidth() // 3) * 2, y := self.TerminalHeight() // 4 + 4, credits_screen)
        self.DrawText(t := "Alex J.", (self.Color.WHITE, self.Color.BACKGROUND), x - len(t) // 2, y + 1, credits_screen)
        self.DrawText(t := "<The Design Helper>", (self.Color.GRAY, self.Color.BACKGROUND), x - len(t) // 2, y + 2, credits_screen)

        self.DrawChar('@', (self.Color.LIGHT_YELLOW, self.Color.BACKGROUND), x := self.TerminalWidth() // 2, y := self.TerminalHeight() // 2 + 3, credits_screen)
        self.DrawText(t := "Michael H.", (self.Color.WHITE, self.Color.BACKGROUND), x - len(t) // 2, y + 1, credits_screen)
        self.DrawText(t := "<The Emotional Support>", (self.Color.GRAY, self.Color.BACKGROUND), x - len(t) // 2, y + 2, credits_screen)

        return True
    
    def GenerateSolidsMap(self):
        # used for pathfinding and fov
        solids = np.array([[ 0 for _ in range(self.current_map.width) ] for _ in range(self.current_map.height)])
        solids[:] = True

        for x in range(self.current_map.width):
            for y in range(self.current_map.height):
                if self.current_map.data.GetAt(x, y).symbol == '#' or any([e.solid and e.x == x and e.y == y for e in self.current_map.entities]):
                    solids[y, x] = False
        
        self.solids = solids

    def HandleTextInput(self):
        # used for things like picking names of things
        if self.HasTextCache():
            self.user_text_input += self.TextCache()
        elif self.KeyPressed(K_BACKSPACE):
            self.user_text_input = self.user_text_input[:-1]

    def HandleMoveAndInteract(self):
        # does what it says basically
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
                self.advance_time = True
                self.action_time = self.player.speed

                if abs(attempt_move_x - self.player.x) and abs(attempt_move_y - self.player.y): # diagonal movement
                    self.action_time = int( self.action_time * 1.4 )

                self.player.x = attempt_move_x
                self.player.y = attempt_move_y
        
        return None
    
    def AdvanceTime(self):
        # TODO: make more advanced time system
        for e in self.current_map.entities:
            e.waited_time += self.action_time
            e.OnMyTurn(self)

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
        # sets the direction x and y variables based on what key we pressed
        # returns true if no longer waiting for a direction (key has been pressed)
        if self.waiting_for_direction:
            self.waiting_for_direction = False

            if   self.KeyPressed(K_KP8) or self.KeyPressed(K_UP)   : self.direction_x, self.direction_y = + 0, - 1
            elif self.KeyPressed(K_KP9)                            : self.direction_x, self.direction_y = + 1, - 1
            elif self.KeyPressed(K_KP6) or self.KeyPressed(K_RIGHT): self.direction_x, self.direction_y = + 1, + 0
            elif self.KeyPressed(K_KP3)                            : self.direction_x, self.direction_y = + 1, + 1
            elif self.KeyPressed(K_KP2) or self.KeyPressed(K_DOWN) : self.direction_x, self.direction_y = + 0, + 1
            elif self.KeyPressed(K_KP1)                            : self.direction_x, self.direction_y = - 1, + 1
            elif self.KeyPressed(K_KP4) or self.KeyPressed(K_LEFT) : self.direction_x, self.direction_y = - 1, + 0
            elif self.KeyPressed(K_KP7)                            : self.direction_x, self.direction_y = - 1, - 1
            else: self.waiting_for_direction = True

            return not self.waiting_for_direction

        return False

    def OnUpdate(self, delta):
        # called every frame

        if self.first_frame:
            # if we don't do this and the user hits a key to skip the engine intro,
            # the first line of text gets skipped entirely
            self.first_frame = False
            return True

        # gets the 'ScrElement' object from the planet overworld
        self.current_overlapping_element = self.current_planet.overworld.GetAt(self.player.x, self.player.y)

        # TODO: update as more game scenes get implemented.
        if self.current_scene in [GameScene.PLANET_AREA, GameScene.PLANET_OVERWORLD]:
            if len(self.messages):
                # If we pressed any key (basically), remove the first message in the queue

                if self.HasTextCache() or any([self.KeyPressed(x) for x in [K_UP, K_DOWN, K_LEFT, K_RIGHT, K_KP1, K_KP2, K_KP3, K_KP4, K_KP6, K_KP7, K_KP8, K_KP9]]):
                    self.messages.pop(0)
                
                # Quit-out early. this is a choke point for the program
                # the user cannot do anything until they drain the message queue
                
                if len(self.messages) > 0:
                    return True

        # stores what unicode character has been pressed
        # obeys modifiers
        cache = self.TextCache() if self.HasTextCache() else None
        
        if self.current_scene not in [GameScene.MAIN_MENU, GameScene.CREDITS, GameScene.BASE_INFO]:
            if self.KeyPressed(pygame.K_z):
                self.dialogue_manager.on_confirm()
        
        if self.current_scene == GameScene.MAIN_MENU:
            if cache == 'p':
                # TODO : switch this to character creation
                self.current_scene = GameScene.PLANET_OVERWORLD
            elif cache == 'c':
                # move to credits scene
                self.current_scene = GameScene.CREDITS
            elif cache == 'q':
                # quit the game
                return False
        elif self.current_scene == GameScene.CREDITS:
            if cache == 'z':
                # move back to main menu
                self.current_scene = GameScene.MAIN_MENU

        if self.dialogue_manager.has_dialogue():
            return True

        # the dreaded switch case
        match self.current_scene:
            case GameScene.PLANET_OVERWORLD:
                # we can move and interact in the overworld
                self.HandleMoveAndInteract()

                if cache == 'b':
                    # attempt place player base
                    if self.current_overlapping_element.symbol in terrain_symbols:
                        if not self.current_planet.contains_base:
                            # If the player presses 'b' and the current planet does not currently have a base, create one.
                            self.DrawChar(
                                'b',
                                (self.current_overlapping_element.fg, self.Color.BACKGROUND),
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
                # if we aren't holding up the game for a direction to be pressed
                # get what entity we move into (for interaction)
                if not self.waiting_for_direction:
                    move_interact_entity = self.HandleMoveAndInteract()
                else:
                    move_interact_entity = None

                has_direction = self.HandleDirection()

                if has_direction:
                    match self.waiting_action:
                        case Actions.CLOSE_DOOR:
                            # check every entity to see if it is a door/hatch
                            for e in self.current_map.entities:
                                if e.x == self.player.x + self.direction_x and e.y == self.player.y + self.direction_y:
                                    if type(e) in [Door, Hatch]:
                                        if e.solid:
                                            self.AddMessage(f"{'Door' if type(e) == Door else 'Hatch'} is already closed.")
                                        else:
                                            self.AddMessage(f"You close the {'door' if type(e) == Door else 'hatch'}.")

                                            e.Close()

                                            self.advance_time = True

                                            self.action_time = action_times[Actions.CLOSE_DOOR]

                                            self.GenerateSolidsMap()
                                    else:
                                        self.AddMessage("You can't close that!")

                    # reset
                    self.waiting_action = None
                    self.waiting_for_direction = False

                if cache == 'c':
                    # player is attempting to close a door
                    self.waiting_for_direction = True
                    self.waiting_action = Actions.CLOSE_DOOR
                    self.AddMessage("Close door in what direction?")

                if move_interact_entity:
                    # if we move into an entity, interact with it and advance time
                    self.advance_time = True

                    move_interact_entity.PlayerMoveInteract(self, self.player)
                    self.action_time = move_interact_entity.move_interact_time
                    
                    # remove the entity if it has marked itself for removal
                    # (usually upon death)
                    if move_interact_entity.to_remove:
                        self.current_map.entities.remove(move_interact_entity)

                    if type(move_interact_entity) in [Door, Hatch]:
                        # If we open a door, regenerate the solids map
                        self.GenerateSolidsMap()
                
                if self.advance_time:
                    self.AdvanceTime()
            
            case GameScene.PLAYER_BASE:
                # we can move and interact in the base
                self.HandleMoveAndInteract()

                if cache == '<':
                    # player leaves base
                    self.AddMessage("You leave your base.")
                    self.LoadOverworld()
                elif cache == 'b':
                    # move to base info scene
                    self.current_scene = GameScene.BASE_INFO

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
        # go thru each entity and draw it to the game window
        for e in self.current_map.entities:
            self.DrawChar(e.repr.symbol, (e.repr.fg, e.repr.bg), e.x, e.y, self.game_window)

    def OnDraw(self):
        # clear the screen and the game window
        self.Clear(' ', (self.Color.WHITE, self.Color.BACKGROUND))
        self.Clear(' ', (self.Color.WHITE, self.Color.BACKGROUND), self.game_window)
        
        # the other dreaded switch case
        match self.current_scene:
            case GameScene.MAIN_MENU:
                # blit the static menu buffer
                self.BlitBuffer(main_menu, 0, 0)

                for x in range(self.TerminalWidth() - 2):
                    for y in range(self.TerminalHeight() - 2):
                        if self.CharAt(x + 1, y + 1).symbol == " ":
                            self.DrawChar('.', (random.choice([self.Color.DARK_CYAN, self.Color.VERY_DARK_CYAN, self.Color.DARK_GRAY, self.Color.VERY_DARK_GRAY]), self.Color.BLACK), x + 1, y + 1)
                
                return True
            
            case GameScene.CREDITS:
                # blit the static credits buffer
                self.BlitBuffer(credits_screen, 0, 0)

                for x in range(self.TerminalWidth() - 2):
                    for y in range(self.TerminalHeight() - 2):
                        if self.CharAt(x + 1, y + 1).symbol == " ":
                            self.DrawChar('.', (random.choice([self.Color.DARK_MAGENTA, self.Color.VERY_DARK_MAGENTA, self.Color.DARK_GRAY, self.Color.VERY_DARK_GRAY]), self.Color.BLACK), x + 1, y + 1)
                
                return True

            case GameScene.PLANET_OVERWORLD:
                # blit the planet overworld buffer to the game window
                # and put the planet name on the bottom of the screen
                self.BlitBuffer(self.current_planet.overworld, 0, 0, self.game_window)
                self.DrawText(f"{self.current_planet.name} Overworld", (self.Color.WHITE, self.Color.BACKGROUND), 0, self.TerminalHeight() - 1)

            case GameScene.PLANET_AREA:
                # blit the map buffer to the game window
                # and put the area name on the bottom of the screen
                self.BlitBuffer(self.current_map.data, 0, 0, self.game_window)
                self.DrawText(self.current_map.name, (self.Color.WHITE, self.Color.BACKGROUND), 0, self.TerminalHeight() - 1)
            
                self.DrawEntities()

            case GameScene.PLAYER_BASE:
                # blit the base buffer to the game window
                # and put the base name on the bottom of the screen
                self.BlitBuffer(self.current_map.data, 0, 0, self.game_window)
                self.DrawText(self.current_map.name, (self.Color.WHITE, self.Color.BACKGROUND), 0, self.TerminalHeight() - 1)

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
                self.Clear(' ', (self.Color.WHITE, self.Color.BACKGROUND), self.game_window)
                # draw the title
                self.DrawTextLines(
                    [
                        "Base Info",
                        "-"*self.game_window.width,
                    ],
                    (self.Color.YELLOW, self.Color.BACKGROUND), 0, 0,
                    scr = self.game_window
                )
                # draw the left side
                self.DrawTextLines(
                    [
                        f'Name   -',
                        f'Planet -',
                        '',
                        f'Level  -',
                        f'EXP    -',
                    ],
                    (self.Color.WHITE, self.Color.BACKGROUND), 0, 3,
                    scr = self.game_window
                )
                # draw the right side
                self.DrawTextLines(
                    [
                        f'{self.current_map.name}',
                        f'{self.current_planet.name}',
                        '',
                        f'{self.current_map.level}',
                        f'{self.current_map.exp}/{self.current_map.exp_to_level_up}'
                    ],
                    (self.Color.YELLOW, self.Color.BACKGROUND), 10, 3,
                    scr = self.game_window
                )

                # draw a lil window if renaming the base
                if self.renaming_base:
                    self.FillRect(' ', (0, 0), self.game_window.width // 2 - 20, self.game_window.height // 2 - 4, 40, 8, scr = self.game_window)
                    self.DrawRect((self.Color.WHITE, self.Color.BACKGROUND), self.game_window.width // 2 - 20, self.game_window.height // 2 - 4, 40, 8, scr = self.game_window)

                    self.DrawTextLines(["Rename your base to what?", '-' * 39], (self.Color.YELLOW, self.Color.BACKGROUND), self.game_window.width // 2 - 19, self.game_window.height // 2 - 3, scr=self.game_window)

                    self.DrawText(self.user_text_input + '_', (self.Color.WHITE, self.Color.BACKGROUND), self.game_window.width // 2 - 19, self.game_window.height // 2 - 1, scr = self.game_window)

                self.DrawText(t := "n - Rename Base     z - Exit", (self.Color.WHITE, self.Color.BACKGROUND), self.TerminalWidth() - (len(t) + 1), self.TerminalHeight() - 1)

        show_dialogue = False
        if self.current_scene != GameScene.BASE_INFO:
            show_dialogue = True

            # draw the '@' for the player
            self.DrawChar('@', (self.Color.LIGHT_MAGENTA, self.Color.BACKGROUND), self.player.x, self.player.y, self.game_window)

            if self.current_map:
                # compute fov
                fov = tcod.map.compute_fov(self.solids, (self.player.y, self.player.x), self.player.sight_distance, algorithm=tcod.constants.FOV_DIAMOND)

                active_visibility = [False for _ in range(len(self.current_map.visibility))]

                # black out or darken cells based on the visibility
                for x in range(self.game_window.width):
                    for y in range(self.game_window.height):
                        if fov[y, x] and self.current_map:
                            self.current_map.visibility[y * self.current_map.width + x] = True
                            active_visibility[y * self.current_map.width + x] = True
                        
                        if self.current_map and not self.current_map.visibility[y * self.current_map.width + x]:
                            self.DrawChar('?', (self.Color.VERY_DARK_GRAY, self.Color.BACKGROUND), x, y, self.game_window)
                        
                        if self.current_map and self.current_map.visibility[y * self.current_map.width + x] and not active_visibility[y * self.current_map.width + x]:
                            e = self.game_window.GetAt(x, y)
                            self.DrawChar(e.symbol, (self.DarkenColor(e.fg), self.DarkenColor(e.bg)), x, y, self.game_window)

            if len(self.messages):
                # If we have messages, display the first one
                msg = self.messages[0] + (' (more)' if len(self.messages) != 1 else '')

                # split a line that's too long into two lines
                if len(msg) > self.TerminalWidth() - 1:
                    lines = ['']
                    size = 0

                    for el in msg.split(' '):
                        lines[-1] += el + ' '

                        size += len(el) + 1

                        if size > self.TerminalWidth() - 5:
                            lines.append('')
                            size = 0
                else:
                    lines = [msg]

                # draw the text
                self.DrawTextLines(lines[:2], (self.Color.WHITE, self.Color.BACKGROUND), 0, 0)
            elif self.current_scene == GameScene.PLANET_OVERWORLD:
                # Otherwise, attempt to show the generic description of the tile we are on
                if self.current_overlapping_element.symbol in overworld_tile_descriptions:
                    self.DrawText(overworld_tile_descriptions[self.current_overlapping_element.symbol], (self.Color.WHITE, self.Color.BACKGROUND), 0, 0)


        # put the game window onto the main screen
        self.BlitBuffer(self.game_window, 0, 2)

        if show_dialogue:
            self.dialogue_manager.draw(self)

        if DEBUG:
            # highlight the mouse pos and show the pos x and y
            mx, my = self.MousePos()

            self.SetColor((self._scr_buf.GetAt(mx, my).fg, self.Color.WHITE), mx, my)
            self.DrawTextLines([f"{mx, my}"], (self.Color.WHITE, self.Color.BACKGROUND), self.TerminalWidth() - 1, 0, True)

        return True

# create the game object and start the game :)
game = Game(terminal_width, terminal_height)
game.start()