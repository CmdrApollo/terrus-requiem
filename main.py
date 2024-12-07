from pyne.pyne import *
from player import Player
from entity import *
from area_map import *
from ship_chassis import *
from utils import *
from dialogue import DialogueManager
from homeworld import *

import numpy as np
import tcod.map
import tcod.constants

GAME_NAME = "Terrus Requiem"
GAME_VERSION = "InDev v0.0.1"

# these screens are static, so they are stored as buffers for simplicity.
main_menu = PyneEngine.Buffer(terminal_width, terminal_height)
credits_screen = PyneEngine.Buffer(terminal_width, terminal_height)
help_screen1 = PyneEngine.Buffer(terminal_width, terminal_height)
help_screen2 = PyneEngine.Buffer(terminal_width, terminal_height)
help_screen3 = PyneEngine.Buffer(terminal_width, terminal_height)

terrain_symbols = ['"', '+', '&', '~']

DEBUG = False

class GameScene:
    # All of the 'scenes' found in the game

    MAIN_MENU = 0
    CREDITS = 1

    MAIN_SHIP = 2
    CAVE = 3

    INVENTORY = 4
    PLAYER_STATS = 5

    HELP = 6

class Actions:
    # actions that require a direction
    CLOSE_DOOR = 0

action_times = [ 75 ]

class TerrusRequiem(PyneEngine):
    # name of the game and title of the window
    TITLE = GAME_NAME

    def __init__(self, terminal_width=terminal_width, terminal_height=terminal_height, target_size=(1600, 900)):
        super().__init__(terminal_width, terminal_height, target_size)

        # where most things get rendered besides the 5 lines of text
        self.game_window = self.Buffer(self.TerminalWidth(), self.TerminalHeight() - 5)
    
        self.player = Player(self, self.game_window.width // 2, self.game_window.height // 2)

        # used for the pseudo-state machine
        self.current_scene = GameScene.MAIN_MENU

        self.main_map = MainMap(self)

        # used for collisions and things
        self.current_map = self.main_map
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

        self.prev_scene = None
        self.help_screen = 0
        self.creation_screen = 0

        self.GenerateSolidsMap()

    # add messages to the queue
    def AddMessage(self, message):
        self.messages.append(message)

    def RenderBook(self, title, text, scr=None):
        self.DrawText(t := title, (self.Color.WHITE, self.Color.BACKGROUND), self.TerminalWidth() - len(t), 0, scr)
        self.DrawRect((self.Color.YELLOW, self.Color.BACKGROUND), 5, 2, 65, 25, scr=scr)
        self.DrawTextLines(text, (self.Color.WHITE, self.Color.BACKGROUND), 6, 3, scr=scr)

    def OnConstruct(self):
        self.LoadAudio("main_theme", ["assets", "audio", "main_theme.wav"])

        self.LoadAudio("hit_1", ["assets", "audio", "hit", "hit_1.wav"])
        self.LoadAudio("hit_2", ["assets", "audio", "hit", "hit_2.wav"])
        self.LoadAudio("hit_3", ["assets", "audio", "hit", "hit_3.wav"])

        self.PlaySong("main_theme")

        # === GENERATE MAIN MENU ===

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
        
        # === GENERATE CREDITS ===

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

        # === GENERATE HELP 1 ===
        self.Clear(' ', (self.Color.WHITE, self.Color.BACKGROUND), help_screen1)
        self.RenderBook("Help 1/2", [
            "General =======================|================================",
            "[h] - Help                     |[arrows/numpad] - Move          ",
            "[>] - Enter Area               |[<] - Leave Area                ",
            "[space] - Advance Dialogue     |[z] - Close Menu                ",
            "                               |                                ",
            "Overworld =====================|================================",
            "[b] - Place Base               |                                ",
            "                               |                                ",
            "Help ==========================|================================",
            "[1/2] - Change Screen          |[z] - Return to Game            ",
            "                               |                                ",
            "Planet Base ===================|================================",
            "[b] - Base Info Screen         |[<] - Leave Base                ",
            "                               |                                ",
            "Base Info =====================|================================",
            "[n] - Rename Base              |[z] - Return to Game            ",
            "                               |                                ",
            "                               |                                ",
            "                               |                                ",
            "                               |                                ",
            "                               |                                ",
            "                               |                                ",
            "                               |                                ",
            "                               |                                ",
        ], help_screen1)
        # === GENERATE HELP 2 ===
        self.Clear(' ', (self.Color.WHITE, self.Color.BACKGROUND), help_screen2)
        self.RenderBook("Help 2/2", [
            "                               |                                ",
            "                               |                                ",
            "                               |                                ",
            "                               |                                ",
            "                               |                                ",
            "                               |                                ",
            "                               |                                ",
            "                               |                                ",
            "                               |                                ",
            "                               |                                ",
            "                               |                                ",
            "                               |                                ",
            "                               |                                ",
            "                               |                                ",
            "                               |                                ",
            "                               |                                ",
            "                               |                                ",
            "                               |                                ",
            "                               |                                ",
            "                               |                                ",
            "                               |                                ",
            "                               |                                ",
            "                               |                                ",
            "                               |                                ",
        ], help_screen2)
        # === GENERATE HELP 3 ===
        self.Clear(' ', (self.Color.WHITE, self.Color.BACKGROUND), help_screen3)
        self.RenderBook("Help 3/2", [
            "Hey! Thank you so so much for  |                                ",
            "playing my game, it really     |                                ",
            "means so much to me! This game |                                ",
            "has been a really important    |                                ",
            "part of my life for a while now|                                ",
            "and I love that I get to share |                                ",
            "it with you! As I'm writing    |                                ",
            "this, the game is still in     |                                ",
            "early stages (the code is only |                                ",
            "around 2000 lines so far), but |                                ",
            "I'm still really happy with the|                                ",
            "progress that I've made. I     |                                ",
            "can't wait to finish this game |                                ",
            "and release it to the world.   |                                ",
            "This whole experience has      |                                ",
            "already shaped me as a person  |                                ",
            "and I can't wait to see where I|                                ",
            "go from here. I love you all   |                                ",
            "and wish you all the best of   |                                ",
            "luck!                          |                                ",
            "                               |                                ",
            "                               |                                ",
            "                         -Elly |                                ",
            "                               |                                ",
        ], help_screen3)

        self.LoadWorld()

        self.current_scene = GameScene.MAIN_MENU
        
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
        
        self.player.x = self.current_map.player_start_x
        self.player.y = self.current_map.player_start_y

    def LoadWorld(self):
        self.current_scene = GameScene.MAIN_SHIP
        self.current_map = self.main_map

        self.player.x = self.current_map.x
        self.player.y = self.current_map.y

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

    def HandleHelpScreen(self):
        if self.KeyPressed(K_h):
            self.prev_scene = self.current_scene
            self.current_scene = GameScene.HELP

    def OnUpdate(self, delta):
        # called every frame

        if self.first_frame:
            # if we don't do this and the user hits a key to skip the engine intro,
            # the first line of text gets skipped entirely
            self.first_frame = False
            return True

        # TODO: update as more game scenes get implemented.
        if self.current_scene  == GameScene.MAIN_SHIP:
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
        
        if self.current_scene not in [GameScene.MAIN_MENU, GameScene.CREDITS, GameScene.HELP]:
            if self.KeyPressed(pygame.K_SPACE):
                self.dialogue_manager.on_confirm()
        
        if self.current_scene == GameScene.MAIN_MENU:
            if cache == 'p':
                self.current_scene = GameScene.MAIN_SHIP
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
        elif self.current_scene == GameScene.HELP:
            if cache == 'z':
                # move back to game
                self.current_scene = self.prev_scene
                return True
            elif cache == '1':
                self.help_screen = 0
            elif cache == '2':
                self.help_screen = 1
            elif cache == '3':
                self.help_screen = 2

        if self.dialogue_manager.has_dialogue():
            return True

        # the dreaded switch case
        match self.current_scene:
            case GameScene.MAIN_SHIP:
                # we can move and interact in the overworld
                self.HandleHelpScreen()
                self.HandleMoveAndInteract()

                if cache == '>':
                    # player is attempting to enter an area
                    
                    for area in self.current_planet.areas:
                        if area.x == self.player.x and area.y == self.player.y:
                            self.LoadMap(area, self.current_overlapping_element.symbol == 'b')

                            self.AddMessage(f"You entered '{self.current_map.name}'.")

                            self.GenerateSolidsMap()

                            break
           
            case GameScene.CAVE:
                self.HandleHelpScreen()
                self.HandleMoveAndInteract()
            
            case GameScene.INVENTORY:
                self.HandleHelpScreen()
            
            case GameScene.PLAYER_STATS:
                self.HandleHelpScreen()

        return True
    
    def DrawEntities(self):
        # go thru each entity and draw it to the game window
        for e in self.current_map.entities:
            self.DrawChar(e.repr.symbol, (e.repr.fg, e.repr.bg), e.x, e.y, self.game_window)

    def OnDraw(self):
        show_dialogue = False

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

            case GameScene.MAIN_SHIP:
                # blit the planet overworld buffer to the game window
                # and put the planet name on the bottom of the screen
                self.BlitBuffer(self.current_map.data, 0, 0, self.game_window)
                self.DrawText(f"{self.current_map.name}", (self.Color.WHITE, self.Color.BACKGROUND), 0, self.TerminalHeight() - 1)

                self.DrawEntities()
            
            case GameScene.CAVE:
                pass
            
            case GameScene.INVENTORY:
                pass
            
            case GameScene.PLAYER_STATS:
                pass

            case GameScene.HELP:
                self.BlitBuffer([help_screen1, help_screen2, help_screen3][self.help_screen], 0, 0)
                
                return True
            
        if self.current_scene not in [GameScene.HELP, GameScene.INVENTORY, GameScene.PLAYER_STATS]:
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
game = TerrusRequiem(terminal_width, terminal_height)
game.start()