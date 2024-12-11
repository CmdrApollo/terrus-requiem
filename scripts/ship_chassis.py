from pyne.pyne import *
from .utils import *
from .ship import *

def generate_chassis_Z800(engine):
    buffer = BufferWithEntities(100, 50)

    engine.Clear(' ', (engine.Color.WHITE, engine.Color.BACKGROUND), buffer)

    engine.FillRect('.', (engine.Color.GRAY, engine.Color.BACKGROUND), 20, 7, 25, 8, buffer)
    engine.FillRect('.', (engine.Color.GRAY, engine.Color.BACKGROUND), 18, 9, 2, 4, buffer)
    engine.FillRect('.', (engine.Color.GRAY, engine.Color.BACKGROUND), 48, 8, 8, 6, buffer)
    engine.FillRect('.', (engine.Color.GRAY, engine.Color.BACKGROUND), 56, 9, 2, 4, buffer)

    buffer.entities.append(Hatch(0, 4))
    buffer.entities.append(Hatch(0, 5))

    buffer.entities.append(Hatch(29, 4))
    buffer.entities.append(Hatch(29, 5))

    engine.DrawHLine((engine.Color.GRAY, engine.Color.BACKGROUND), 40, 10, 50, '.', scr=buffer)
    engine.DrawHLine((engine.Color.GRAY, engine.Color.BACKGROUND), 40, 11, 50, '.', scr=buffer)

    buffer.entities.append(ControlPanel(40, 4))

    wallify(buffer, engine)

    final = crop(buffer, engine)

    engine.DrawChar('.', (engine.Color.GRAY, engine.Color.BACKGROUND), 0, 4, scr=final)
    engine.DrawChar('.', (engine.Color.GRAY, engine.Color.BACKGROUND), 0, 5, scr=final)

    chassis = ShipChassis(final.width, final.height, ShipClass.CARGO, 'Z800')
    chassis.data = final.data
    chassis.entities = final.entities

    return chassis

def generate_chassis_X40(engine):
    buffer = BufferWithEntities(100, 50)

    engine.Clear(' ', (engine.Color.WHITE, engine.Color.BACKGROUND), buffer)

    engine.FillRect('.', (engine.Color.GRAY, engine.Color.BACKGROUND), 10, 5, 2, 10, buffer)
    engine.FillRect('.', (engine.Color.GRAY, engine.Color.BACKGROUND), 12, 6, 2, 8, buffer)
    engine.FillRect('.', (engine.Color.GRAY, engine.Color.BACKGROUND), 14, 7, 4, 6, buffer)
    engine.FillRect('.', (engine.Color.GRAY, engine.Color.BACKGROUND), 18, 5, 2, 10, buffer)
    engine.FillRect('.', (engine.Color.GRAY, engine.Color.BACKGROUND), 20, 6, 2, 8, buffer)
    engine.FillRect('.', (engine.Color.GRAY, engine.Color.BACKGROUND), 22, 7, 2, 6, buffer)
    engine.FillRect('.', (engine.Color.GRAY, engine.Color.BACKGROUND), 24, 8, 2, 4, buffer)
    engine.FillRect('.', (engine.Color.GRAY, engine.Color.BACKGROUND), 26, 9, 2, 2, buffer)
    engine.FillRect('.', (engine.Color.GRAY, engine.Color.BACKGROUND), 3, 8, 6, 4, buffer)
    engine.FillRect('.', (engine.Color.GRAY, engine.Color.BACKGROUND), 1, 9, 2, 2, buffer)

    buffer.entities.append(Hatch(0, 5))
    buffer.entities.append(Hatch(0, 6))

    buffer.entities.append(Hatch(9, 5))
    buffer.entities.append(Hatch(9, 6))

    buffer.entities.append(ControlPanel(27, 5))

    wallify(buffer, engine)

    final = crop(buffer, engine)

    engine.DrawChar('.', (engine.Color.GRAY, engine.Color.BACKGROUND), 0, 5, scr=final)
    engine.DrawChar('.', (engine.Color.GRAY, engine.Color.BACKGROUND), 0, 6, scr=final)

    engine.DrawChar('.', (engine.Color.GRAY, engine.Color.BACKGROUND), 9, 5, scr=final)
    engine.DrawChar('.', (engine.Color.GRAY, engine.Color.BACKGROUND), 9, 6, scr=final)

    chassis = ShipChassis(final.width, final.height, ShipClass.FIGHTER, 'X40')
    chassis.data = final.data
    chassis.entities = final.entities

    return chassis