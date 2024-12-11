from pyne.pyne import PyneEngine
from .utils import *

class PartType:
    FUEL_TANK = 0
    THRUSTERS = 1
    LANDING_GEAR = 2
    AIR_PRESSURIZER = 3
    HEAT_REGULATOR = 4
    POWER_GENERATOR = 5
    CONTROL_PANEL = 6
    THRUSTER_ACTUATORS = 7

    AUTO_NAV = 8
    COMMUNICATION_SYSTEM = 9
    BACKUP_GENERATOR = 10
    RADAR = 11
    HYPERDRIVE = 12

class ShipClass:
    CARGO = 0
    FUELER = 1
    FIGHTER = 2
    TRANSPORT = 3

class ShipPart:
    def __init__(self, part_type):
        self.part_type = part_type

class ShipChassis(BufferWithEntities):
    def __init__(self, width: int, height: int, classification: int, model: str):
        super().__init__(width, height)

        self.classification = classification
        self.model = model

class Ship:
    def __init__(
            self,

            classification       : int      = 0,
            model                : str      = '',

            chassis              : ShipChassis  = None,

            fuel_tank            : ShipPart = None,
            thrusters            : ShipPart = None,
            landing_gear         : ShipPart = None,
            air_pressurizer      : ShipPart = None,
            heat_regulator       : ShipPart = None,
            power_generator      : ShipPart = None,
            control_panel        : ShipPart = None,
            thruster_actuators   : ShipPart = None,
  
            auto_nav             : ShipPart = None,
            communication_system : ShipPart = None,
            backup_generator     : ShipPart = None,
            radar                : ShipPart = None,
            hyperdrive           : ShipPart = None
        ):
        self.classification = classification
        self.model = model

        self.chassis = chassis

        self.fuel_tank            = fuel_tank            
        self.thrusters            = thrusters            
        self.landing_gear         = landing_gear         
        self.air_pressurizer      = air_pressurizer      
        self.heat_regulator       = heat_regulator       
        self.power_generator      = power_generator      
        self.control_panel        = control_panel        
        self.thruster_actuators   = thruster_actuators   

        self.auto_nav             = auto_nav             
        self.communication_system = communication_system 
        self.backup_generator     = backup_generator     
        self.radar                = radar                
        self.hyperdrive           = hyperdrive

starting_ship = Ship(ShipClass.CARGO, 'Fura 80-1')