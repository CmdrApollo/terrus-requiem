VERSION = "0.1"

import pygame
import math
import os
import sys

from pygame.locals import *
from pyne.character import *
from pyne.pyne_logo import *

from pyne.AudioHandler import AudioHandler

LMB = 0
MMB = 1
RMB = 2

pygame.init()

FULLSCREEN = False

class Status:
    BOOT = 0
    IDLE = 1

class PyneEngine:
    TITLE = ""

    class Buffer:
        def __init__(self, width: int, height: int):
            self.width = width
            self.height = height

            self.data: list[ScrElement] = [ScrElement(None, PyneEngine.Color.WHITE, PyneEngine.Color.BACKGROUND) for _ in range(self.width * self.height)]

            self.p = lambda x, y: y * self.width + x
        
        def GetAt(self, x, y):
            if x < 0 or x > self.width - 1 or y < 0 or y > self.height - 1:
                return None
            return self.data[self.p(x, y)]

    def __init__(self, terminal_width=76, terminal_height=28, target_size=(1290, 720)):
        self._status = Status.BOOT
        self._boot_timer = 0
        self._stall_timer = 0

        self._width = terminal_width
        self._height = terminal_height

        font = "mono_font_roguelike.ttf"

        point = 12
        for _ in range(0x40):
            s = pygame.font.Font(font, point).size('M')
            
            if s[1] * terminal_height == target_size[1]:
                break

            elif s[1] * terminal_height < target_size[1]:
                if pygame.font.Font(font, point + 1).size('M')[1] * terminal_height > target_size[1]:
                    break
                point += 1
                
        # point = int(point * 0.8)

        self._font = pygame.font.Font(font, point)
        self._point = point

        self._single_char_size = pygame.Vector2(self._font.render('M', True, self.Color.BACKGROUND).get_size())

        self._scr_buf = self.Buffer(self._width, self._height)

        self._window = pygame.display.set_mode((self._single_char_size.x * self._width, self._single_char_size.y * self._height), pygame.FULLSCREEN if FULLSCREEN else 0)

        self._character_cache = {

        }

        self._p = lambda x, y: y * self._width + x

        self._pressed = [False for _ in range(255)]
        self._released = [False for _ in range(255)]
        self._held = [False for _ in range(255)]

        self._mouse_pressed = [False for _ in range(3)]
        self._mouse_released = [False for _ in range(3)]
        self._mouse_held = [False for _ in range(3)]

        self._text_edit_cache = ' '

        self._text_edit = False

        self._audio_handler = AudioHandler({})

        self.lines = pygame.image.load('scanlines_full.png').convert_alpha()

        pygame.key.set_repeat(500, 75)

    def LoadAudio(self, name, path):
        self._audio_handler.update_sounds({ name: pygame.mixer.Sound(os.path.join(*path)) })

    def PlaySound(self, name):
        if name in self._audio_handler.sounds:
            self._audio_handler.play_sound(name)
        else:
            print(f"Audio handler has no clip named '{name}'")

    def PlaySong(self, name, loops=-1):
        if name in self._audio_handler.sounds:
            self._audio_handler.play_song(name, loops)
        else:
            print(f"Audio handler has no clip named '{name}'")

    def GetAudioHandler(self):
        return self._audio_handler

    def TerminalWidth(self): return self._width
    def TerminalHeight(self): return self._height

    class Color:
        WHITE = '#ffffff'
        BLACK = '#000000'
        
        BACKGROUND = '#000000'

        RED = '#ff0000'
        GREEN = '#00ff00'
        BLUE = '#0000ff'

        YELLOW = '#ffff00'
        MAGENTA = '#ff00ff'
        CYAN = '#00ffff'

        LIGHT_RED = '#ff8080'
        LIGHT_GREEN = '#80ff80'
        LIGHT_BLUE = '#8080ff'

        LIGHT_YELLOW = '#ffff80'
        LIGHT_MAGENTA = '#ff80ff'
        LIGHT_CYAN = '#80ffff'

        GRAY = '#808080'
        DARK_GRAY = '#404040'
        VERY_DARK_GRAY = "#202020"

        DARK_RED = '#800000'
        DARK_GREEN = '#008000'
        DARK_BLUE = '#000080'

        DARK_YELLOW = '#808000'
        DARK_MAGENTA = '#800080'
        DARK_CYAN = '#008080'

        VERY_DARK_RED = '#400000'
        VERY_DARK_GREEN = '#004000'
        VERY_DARK_BLUE = '#000040'

        VERY_DARK_YELLOW = '#404000'
        VERY_DARK_MAGENTA = '#400040'
        VERY_DARK_CYAN = '#004040'

        ORANGE = '#ff8000'
        BROWN = '#804000'
        DARK_BROWN = '#402000'
        VERY_DARK_BROWN = "#201000"

    def DarkenColor(self, color):
        r, g, b = int(color[1] + color[2], 16), int(color[3] + color[4], 16), int(color[5] + color[6], 16)

        return '#' + ''.join([hex(int(x * 0.75)).removeprefix('0x').rjust(2, '0') for x in [r,g,b]])

    def OnConstruct(self):
        pass

    def OnUpdate(self, delta):
        pass

    def OnDraw(self):
        pass

    def Clear(self, symbol, c_pair, scr=None):
        scr = scr if scr else self._scr_buf
        for x in range(scr.width):
            for y in range(scr.height):
                scr.data[scr.p(x, y)].symbol = symbol
                scr.data[scr.p(x, y)].fg     = c_pair[0]
                scr.data[scr.p(x, y)].bg     = c_pair[1]

    def ColorClear(self, c_pair, scr=None):
        scr = scr if scr else self._scr_buf
        for x in range(scr.width):
            for y in range(scr.height):
                scr.data[scr.p(x, y)].fg     = c_pair[0]
                scr.data[scr.p(x, y)].bg     = c_pair[1]

    def ReplaceChar(self, replacee, symbol, c_pair, scr=None):
        scr = scr if scr else self._scr_buf
        for x in range(scr.width):
            for y in range(scr.height):
                if scr.data[scr.p(x, y)].symbol == replacee:
                    scr.data[scr.p(x, y)].symbol = symbol
                    scr.data[scr.p(x, y)].fg     = c_pair[0]
                    scr.data[scr.p(x, y)].bg     = c_pair[1]

    def DrawChar(self, char, c_pair, x, y, scr=None):
        scr = scr if scr else self._scr_buf
        if 0 <= x     < self._width:
            if 0 <= y < self._height:
                try:
                    scr.data[scr.p(x, y)].symbol = char
                    scr.data[scr.p(x, y)].fg     = c_pair[0]
                    scr.data[scr.p(x, y)].bg     = c_pair[1]
                except:
                    pass

    def SetColor(self, c_pair, x, y, scr=None):
        scr = scr if scr else self._scr_buf
        if 0 <= x     < self._width:
            if 0 <= y < self._height:
                try:
                    scr.data[scr.p(x, y)].fg     = c_pair[0]
                    scr.data[scr.p(x, y)].bg     = c_pair[1]
                except:
                    pass

    def DrawText(self, text, c_pair, x, y, scr=None):
        scr = scr if scr else self._scr_buf
        for i in range(len(text)):
            if 0 <= x + i < self._width:
                if 0 <= y < self._height:
                    self.DrawChar(text[i], c_pair, x + i, y, scr)

    def DrawTextLines(self, lines, c_pair, x, y, right_align = False, scr=None):
        scr = scr if scr else self._scr_buf
        for i in range(len(lines)):
            if 0 <= x         < self._width:
                if 0 <= y + 1 < self._height:
                    self.DrawText(t := lines[i], c_pair, x - len(t) if right_align else x, y + i, scr)

    def DrawHLine(self, c_pair, x1, y, x2, char = '─', scr=None):
        scr = scr if scr else self._scr_buf
        for i in range(x2 - x1):
            self.DrawChar(char, c_pair, x1 + i, y, scr)

    def DrawVLine(self, c_pair, x, y1, y2, char = '│', scr=None):
        scr = scr if scr else self._scr_buf
        for i in range(y2 - y1):
            self.DrawChar(char, c_pair, x, y1 + i, scr)

    def DrawRect(self, c_pair, x, y, w, h, char=None, scr=None):
        scr = scr if scr else self._scr_buf
        self.DrawHLine(c_pair, x + 1, y, x + w, char if char else '─', scr=scr)
        self.DrawHLine(c_pair, x + 1, y + h, x + w, char if char else '─', scr=scr)

        self.DrawVLine(c_pair, x, y + 1, y + h, char if char else '│', scr=scr)
        self.DrawVLine(c_pair, x + w, y + 1, y + h, char if char else '│', scr=scr)

        self.DrawChar(char if char else '┌', c_pair, x, y, scr=scr)
        self.DrawChar(char if char else '└', c_pair, x, y + h, scr=scr)

        self.DrawChar(char if char else '┐', c_pair, x + w, y, scr=scr)
        self.DrawChar(char if char else '┘', c_pair, x + w, y + h, scr=scr)
    
    def FillRect(self, char, c_pair, x, y, w, h, scr=None):
        scr = scr if scr else self._scr_buf
        for i in range(w):
            for j in range(h):
                self.DrawChar(char, c_pair, x + i, y + j, scr=scr)
    
    def BlitBuffer(self, buffer, x, y, scr=None):
        scr = scr if scr else self._scr_buf

        for i in range(buffer.width):
            for j in range(buffer.height):
                if 0 <= i + x <= self.TerminalWidth() - 1:
                    if 0 <= j + y <= self.TerminalHeight() - 1:
                        c = buffer.data[buffer.p(i, j)]
                        
                        if c:
                            self.DrawChar(c.symbol, (c.fg, c.bg), i + x, j + y, scr)

    def KeyPressed(self, key):
        return self._pressed[key & 0xff]
    
    def KeyReleased(self, key):
        return self._released[key & 0xff]
    
    def KeyHeld(self, key):
        return self._held[key & 0xff]

    def HasTextCache(self):
        return self._text_edit

    def TextCache(self):
        return self._text_edit_cache

    def MousePressed(self, button): return self._mouse_pressed[button]

    def MouseReleased(self, button): return self._mouse_released[button]

    def MouseHeld(self, button): return self._mouse_held[button]

    def MousePos(self):
        mx, my = pygame.mouse.get_pos()
        return (min(mx, self._window.get_width() - 1) // int(self._single_char_size.x), min(my, self._window.get_height() - 1) // int(self._single_char_size.y))

    def GetTimeSeconds(self):
        return pygame.time.get_ticks() / 1000

    def CharAt(self, x, y):
        return self._scr_buf.data[y * self._width + x]

    def display_buffer(self):
        for x in range(self._width):
            for y in range(self._height):
                char = self._scr_buf.data[self._scr_buf.p(x, y)]

                if (char.symbol, char.fg, char.bg) in self._character_cache:
                    self._window.blit(self._character_cache[(char.symbol, char.fg, char.bg)], (x * self._single_char_size.x, y * self._single_char_size.y))
                else:
                    self._character_cache.update({
                        (char.symbol, char.fg, char.bg): char.draw(self._window, (x * self._single_char_size.x, y * self._single_char_size.y), self._font)
                    })
        self._window.blit(self.lines, (0, 0))
        pygame.display.flip()

    def start(self):
        global FULLSCREEN

        run = True
        clock = pygame.time.Clock()
        
        if os.path.exists('icon.bmp'):
            pygame.display.set_icon(pygame.image.load_basic('icon.bmp'))

        while run:
            delta = clock.tick(30) / 1000

            if delta:
                pygame.display.set_caption(f"{self.TITLE} | Pyne Engine v{VERSION} - {( 1 / delta ):.2f} FPS")

            keys = pygame.key.get_pressed()

            self._text_edit = False

            self._pressed = [False for _ in range(255)]
            self._released = [False for _ in range(255)]
            self._held = [keys[i] for i in range(255)]

            self._mouse_pressed = [False for _ in range(3)]
            self._mouse_released = [False for _ in range(3)]
            self._mouse_held = list(pygame.mouse.get_pressed())

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                elif event.type == pygame.KEYDOWN:
                    if self._status == Status.BOOT:
                        self._status = Status.IDLE
                        self.OnConstruct()
                    else:
                        self._pressed[event.key & 0xff] = True
                elif event.type == pygame.KEYUP:
                    self._released[event.key & 0xff] = True

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button <= 3:
                        self._mouse_pressed[event.button - 1] = True
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button <= 3:
                        self._mouse_released[event.button - 1] = True
                
                elif event.type == pygame.TEXTINPUT:
                    self._text_edit = True
                    self._text_edit_cache = event.text

            if (keys[K_LALT] or keys[K_RALT]) and self.KeyPressed(K_RETURN):
                FULLSCREEN = not FULLSCREEN
                
                self._window = pygame.display.set_mode((self._single_char_size.x * self._width, self._single_char_size.y * self._height), pygame.FULLSCREEN if FULLSCREEN else 0)

            if self._status == Status.BOOT:
                if self._boot_timer >= 5:
                    self._stall_timer += delta * 1.2
                    if self._stall_timer >= 4.2:
                        self._status = Status.IDLE


                        # This is the point that we switch from the engine screen to
                        # the user's code, so call OnConstruct
                        self.OnConstruct()
                else:
                    self._boot_timer = min(self._boot_timer + delta * 1.5, 5)
                
                self.Clear(' ', (self.Color.WHITE, self.Color.BACKGROUND))
                
                bt = (self._boot_timer / 5)

                self.DrawTextLines(LOGO, (self.Color.BROWN, self.Color.BACKGROUND), self._width // 2 - 5, int((self._height // 2 + 5) * bt) - 10)
                self.DrawText("   ^^^^", (self.Color.GREEN, self.Color.BACKGROUND), self._width // 2 - 5, int((self._height // 2 + 5) * bt) - 10)
                self.DrawText("  ENGINE", (self.Color.GREEN, self.Color.BACKGROUND), self._width // 2 - 5, self._height - int((self._height // 2) * bt) + 4)

                if self._stall_timer > 0:
                    self.DrawText(PYNE[int(((min(self._stall_timer, 3 - 1e-08) * 6) / 18) * len(PYNE))], (self.Color.GREEN, self.Color.BACKGROUND), self._width // 2 - 2, self._height // 2 - 5)
        
            else:
                if not self.OnUpdate(delta):
                    run = False

                self.OnDraw()

            self.display_buffer()