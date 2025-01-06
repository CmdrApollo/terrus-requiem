from pyne.pyne import PyneEngine
from scripts.area_map import Cave

class Test(PyneEngine):
    TITLE = "Test"
    def __init__(self, terminal_width=200, terminal_height=80, target_size=(1600, 900)):
        super().__init__(terminal_width, terminal_height, target_size)
        self.ship = Cave("Test", self, 1, 200, 80)
    
    def OnUpdate(self, delta):
        return True

    def OnDraw(self):
        self.BlitBuffer(self.ship.data, 0, 0)
        return True

Test().start()