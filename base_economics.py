from abc import ABC
from errors import BadArgumentFromListErrorCheck, NonNegativeIntegerCheck
from fixed_names import damage_types, DC_types, roll_types, action_times
from random import randint


class BaseResource(ABC):
    def __init__(self):
        super().__init__()
        self.used = False

    def Execute(self):
        self.used = True

    def Reset(self):
        self.used = False
        

class SpellSlot(BaseResource):
    def __init__(self, level: int):
        super().__init__()

        self.level = level


class SpellSlotLevel:
    def __init__(self, level: int, n_slots: int):
        self.slots = [SpellSlot(level)] * n_slots

    def __repr__(self):
        return "  ".join(["[X]" if x.used else "[ ]" for x in self.slots])

    def n_remaining(self):
        return sum([not(x.used) for x in self.slots])
    
    def consume_slot(self,
                     graceful: bool = True):
        if self.n_remaining() <= 0:
            if graceful:
                return False
            else:
                raise ValueError("There are no spell slots remaining.")
            
        available_slots = [x for x in self.slots if not x.used]
        return available_slots[0].Execute()
        
    def refresh_slots(self):
        return [x.Reset() for x in self.slots]


class InventoryItem(BaseResource):
    def __init__(self):
        super().__init__()


class Dice(ABC):
    def __init__(self, n: int):
        super().__init__()
        self.n = n
        self.expected_value = 1/2 * (n + 1)
        self.variance = 1/12 * (n - 1) ** 2
    
    def __repr__(self):
        return "d%s" % self.n

    def Roll(self, simulated: bool = False):
        if simulated:
            return randint(1, self.n)
        else:
            return self.expected_value


class StatusEffect(ABC):
    def __init__(self, 
                 name: str):
        super().__init__()
        self.name = name

    def __repr__(self):
        return self.name


class TurnAction(BaseResource):
    def __init__(self,
                 name: str,
                 action_time: str,
                 is_combat: bool,
                 roll_type: str,
                 damage_die: Dice = None,
                 n_damage_die: int = None,
                 flat_damage: int = None,
                 half_damage_on_fail: bool = False,
                 n_hit_rolls: int = None,
                 damage_type: str = None,
                 n_uses: int = None,
                 utility: int = None,
                 imposed_status: StatusEffect = None,
                 hit_bonus: int = None,
                 DC: int = None,
                 DC_type: str = None):
        super().__init__()

        self.name = name

        BadArgumentFromListErrorCheck(action_time, action_times)
        self.action_time = action_time
        
        self.n_uses = self.validate_numeric_argument(n_uses)
        self.is_combat = is_combat

        BadArgumentFromListErrorCheck(roll_type, roll_types)
        self.roll_type = roll_type
        self.hit_bonus = hit_bonus
        self.imposed_status = imposed_status
        self.half_damage_on_fail = half_damage_on_fail
        self.utility = utility
        self.DC = DC

        self.damage_die = None if damage_die is None else damage_die
        self.DC_type = self.validate_alpha_argument(DC_type, DC_types)
        self.n_damage_die = self.validate_numeric_argument(n_damage_die)
        self.flat_damage = self.validate_numeric_argument(flat_damage)
        self.n_hit_rolls = self.validate_numeric_argument(n_hit_rolls)
        self.damage_type = self.validate_alpha_argument(damage_type, damage_types)


    def __repr__(self):
        if self.roll_type == "hit":
            repr_string = "%s (+%s): %s %s%s" % (self.name, 
                                            self.hit_bonus, 
                                            self.damage_type,
                                            self.n_damage_die,
                                            self.damage_die)
        elif self.roll_type == "save":
            if self.damage_die is None:
                repr_string = "%s (%s %s): %s" % (self.name,
                                self.DC_type,
                                self.DC,
                                self.imposed_status)
            else:
                repr_string = "%s (%s %s): %s %s%s" % (self.name,
                                self.DC_type,
                                self.DC,
                                self.damage_type,
                                self.n_damage_die,
                                self.damage_die)
        else:
            if self.damage_die is None:
                repr_string = "%s: %s" % (self.name, self.imposed_status)
            else:
                if self.imposed_status is None:
                    repr_string = "%s: %s %s%s" % (self.name,
                                                    self.damage_type,
                                                    self.n_damage_die,
                                                    self.damage_die)
                else:
                    repr_string = "%s: %s %s%s, %s" % (self.name,
                                                    self.damage_type,
                                                    self.n_damage_die,
                                                    self.damage_die,
                                                    self.imposed_status)
                
        return repr_string

    def validate_numeric_argument(self, passed_argument):
        if passed_argument is None:
            return None
        else:
            NonNegativeIntegerCheck(passed_argument)
            return passed_argument

    def validate_alpha_argument(self, passed_argument, possible_arguments):
        if passed_argument is None:
            return None
        else:
            BadArgumentFromListErrorCheck(passed_argument, possible_arguments)
            return passed_argument
        
    def execute_action(self, simulated: bool = False):
        if self.damage_die is not None:
            return self.damage_die.Roll(simulated = simulated)


class SpellTurnAction(TurnAction):
    def __init__(self,
                 spell_level: int,
                 **kwargs):
        super().__init__(**kwargs)
        if spell_level < 0:
            raise ValueError("spell_level requires a value of at least 0.")
        self.spell_level = spell_level