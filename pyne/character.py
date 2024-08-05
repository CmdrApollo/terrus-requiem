class ScrElement:
    def __init__(self, symbol, fg, bg):
        self.symbol = symbol
        self.fg = fg
        self.bg = bg
    
    def draw(self, win, position, font):
        el = font.render(self.symbol, True, self.fg, self.bg)
        win.blit(el, position)
        return el