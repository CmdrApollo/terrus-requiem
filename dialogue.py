from pyne.pyne import PyneEngine, pygame

class DialogueManager:
    def __init__(self, text_color='white', border_color='white') -> None:
        self.queued_text = []
        self.text_color = text_color
        self.border_color = border_color

    def calculate_bounds(self):
        return max([len(x) for x in self.queued_text[0]]), len(self.queued_text[0])

    def on_confirm(self):
        if len(self.queued_text):
            self.queued_text.pop(0)

    def queue_text(self, text):
        self.queued_text.append(text)

    def has_dialogue(self):
        return bool(len(self.queued_text))

    def draw(self, engine: PyneEngine):
        if self.has_dialogue():
            w, h = self.calculate_bounds()
            w += 1
            h += 2

            x, y = engine.TerminalWidth() // 2 - w // 2, engine.TerminalHeight() // 2 - h // 2

            engine.FillRect(' ', (self.border_color, engine.Color.BLACK), x, y, w, h)
            engine.DrawRect((self.border_color, engine.Color.BLACK), x, y, w, h)
            engine.DrawText(t := self.queued_text[0][0], (self.text_color, engine.Color.BLACK), x + w // 2 - 1 - len(t) // 2, y + 1)
            engine.DrawHLine((self.text_color, engine.Color.BLACK), x + 1, y + 2, x + w)
            engine.DrawTextLines(self.queued_text[0][1:], (self.text_color, engine.Color.BLACK), x + 1, y + 3)

            if len(self.queued_text) > 1 and (pygame.time.get_ticks() // 750) % 2:
                engine.DrawChar(">", (self.text_color, engine.Color.BLACK), x + w - 1, y + 1)