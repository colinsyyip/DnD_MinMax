from abc import ABC
from base_economics import *
from errors import BadArgumentFromListErrorCheck, NonNegativeIntegerCheck
from fixed_names import (all_proficiencies, all_resistances, all_conditions, 
                         all_immunities, all_vulnerabilities, DC_types, full_stat_names)
from math import floor
import pandas as pd

class Character(ABC):
    def __init__(self,
                 name: str,
                 strength: int,
                 dexterity: int,
                 constitution: int,
                 intelligence: int,
                 wisdom: int,
                 charisma: int,
                 hp: int,
                 ac: int,
                 proficiency_bonus: int = 0, 
                 spell_slots: dict = {},
                 half_proficiencies: list[str] = [],
                 st_proficiencies: list[str] = [],
                 proficiencies: list[str] = [],
                 expertise: list[str] = [],
                 resistances: list[str] = [],
                 vulnerabilities: list[str] = [],
                 immunities: list[str] = [],
                 conditions: list[str] = []):
        super().__init__()

        self.name = name
        self.set_stats(STR=strength, 
                       DEX=dexterity, 
                       CON=constitution,
                       INT=intelligence, 
                       WIS=wisdom,
                       CHA=charisma, 
                       MaxHP=hp,
                       AC=ac,
                       Prof_Bonus=proficiency_bonus)

        self.proficiencies = self.set_character_properties(full_options=all_proficiencies,
                                                           Proficiencies=proficiencies,
                                                           Half_Proficiencies=half_proficiencies,
                                                           Expertise=expertise)
        
        self.st_proficiencies = self.set_character_properties(full_options=DC_types,
                                                              ST_Proficiencies=st_proficiencies,
                                                              boolean_value = True)
        self.set_saving_throw_mods()
    
        self.resistances = self.set_character_properties(full_options=all_resistances,
                                                         Resistances=resistances,
                                                         boolean_value = True)

        self.vulnerablities = self.set_character_properties(full_options=all_vulnerabilities,
                                                            Vulnerabilities=vulnerabilities,
                                                            boolean_value = True)

        self.immunities = self.set_character_properties(full_options=all_immunities + all_conditions,
                                                        Immunities=immunities,
                                                        boolean_value = True)
        
        self.conditions = self.set_character_properties(full_options=all_conditions,
                                                        Conditions=conditions,
                                                        boolean_value = True)
        
        self.add_spellslots(spell_slots)
        
        self.abilities = {}
        
    def __repr__(self):
        repr_string = """
        %s:
        STR:%s\tDEX:%s\tCON:%s\tINT:%s\tWIS:%s\tCHA:%s
        AC:%s\tMax HP:%s
        """
        
        return repr_string % (self.name, 
                              self.STR,
                              self.DEX,
                              self.CON,
                              self.INT,
                              self.WIS,
                              self.CHA,
                              self.AC,
                              self.MaxHP)

    def set_stats(self, **kwargs):
        modifier_dict = {}
        for stat, value in kwargs.items():
            NonNegativeIntegerCheck(value)
            if stat in DC_types:
                modifier_dict[stat] = floor((value - 10)/2)
            setattr(self, stat, value)
        self.ability_modifiers = modifier_dict

    def pass_to_dict(self, 
                     edit_dict: dict, 
                     valid_list, 
                     boolean_value: bool, 
                     set_to: bool = True, **kwargs):
        for stat, value_list in kwargs.items():
            if boolean_value:
                if set_to:
                    stat_value = True
                else: 
                    stat_value = False
            else:
                stat_value = stat[0]
            for value in value_list:
                BadArgumentFromListErrorCheck(value, valid_list)
                edit_dict[value] = stat_value
        return edit_dict
    
    def set_character_properties(self, full_options: list, 
                                 boolean_value: bool = False, 
                                 **kwargs):
        if boolean_value:
            fill_value = False
        else:
            fill_value = None
        all_options_dict = {x: fill_value for x in full_options}
        return self.pass_to_dict(edit_dict = all_options_dict,
                                 valid_list = full_options,
                                 boolean_value = boolean_value,
                                 **kwargs)
    
    def toggle_condition(self, 
                         conditions: list[str], 
                         condition_state: bool):
        for condition in conditions:
            self.conditions[condition] = condition_state

    def add_ability(self, ability_name: str, is_spell: bool, **kwargs):
        if is_spell:
            self.abilities[ability_name] = SpellTurnAction(**kwargs)
        else: 
            self.abilities[ability_name] = TurnAction(**kwargs)

    def add_abilities_from_csv(self, file_path, silent: bool = True):
        ability_sheet = pd.read_csv(file_path)
        column_idx = [x not in ("IS_SPELL") for x in ability_sheet.columns]
        for _, r in ability_sheet.iterrows():
            row_sub_dict = r[column_idx].dropna().to_dict()
            row_sub_dict = {k: int(v) if type(v) is float else v for k, v in row_sub_dict.items()}

            if "damage_die" in row_sub_dict:
                row_sub_dict["damage_die"] = Dice(row_sub_dict["damage_die"])
            
            if "imposed_status" in row_sub_dict:
                row_sub_dict['imposed_status'] = StatusEffect(row_sub_dict['imposed_status'])

            if not r['IS_SPELL']:
                row_sub_dict.pop("spell_level")

            self.add_ability(ability_name = r['name'],
                             is_spell = r ['IS_SPELL'],
                             **row_sub_dict)
        
        if silent: 
            return None
        else:
            return self.abilities
        
    def set_saving_throw_mods(self):
        st_mods = {}
        for stat, ability_modifier in self.ability_modifiers.items():
            if self.st_proficiencies[stat]:
                st_mods[stat] = ability_modifier + self.Prof_Bonus
            else: 
                st_mods[stat] = ability_modifier
        self.st_modifiers = st_mods

    def add_spellslots(self,
                       spellslot_dict: dict):
        spellslot_obj_dict = {}
        for level, num in spellslot_dict.items():
            level = int(level)
            if level <= 0:
                continue
            
            spellslot_obj_dict[level] = SpellSlotLevel(level = level,
                                                       n_slots = num)

        self.spellslots = spellslot_obj_dict
