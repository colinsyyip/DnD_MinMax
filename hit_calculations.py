from base_economics import TurnAction, SpellTurnAction
from character import Character
from errors import BadArgumentFromListErrorCheck, NonNegativeIntegerCheck
from fixed_names import action_times, DC_types, damage_types
import numpy as np
import pandas as pd

def calculate_hit_probability(action,
                              opposing_AC: int = None,
                              opposing_ST: int = None,
                              **kwargs):
    if action.roll_type == "hit":
        if opposing_AC is None:
            raise ValueError("Hit rolls must be against an integer value.")
        # NonNegativeIntegerCheck(opposing_AC)
        raw_hit_calculation = (20 - (opposing_AC - action.hit_bonus))/20
        max_corr_hit_probability = min(1, raw_hit_calculation)
        min_corr_hit_probability = max(max_corr_hit_probability, 0.05)

        return min_corr_hit_probability
        
    elif action.roll_type == "save":
        if opposing_ST is None:
            raise ValueError("Saving throw values must be an integer value.")
        
        # NonNegativeIntegerCheck(opposing_ST)
        raw_save_calculation = 1 - (20 - (action.DC - opposing_ST))/20
        max_corr_save_probability = min(1, raw_save_calculation)
        min_corr_save_probability = max(max_corr_save_probability, 0.05)

        return min_corr_save_probability

    else:
        return 1
    

def calculate_expected_hit(action,
                           simulated: bool = False,
                           vulnerable: bool = False,
                           immunity: bool = False,
                           resistance: bool = False,
                           **kwargs):
    if type(action) not in (TurnAction, SpellTurnAction):
        raise ValueError("action must be of type either TurnAction or SpellTurnAction.")
    
    hit_probability = calculate_hit_probability(action, **kwargs)
    if action.damage_die is None: 
        base_die_value = 0
    else:
        if simulated:
            base_die_value = sum([action.damage_die.Roll(True) for _ in range(action.n_damage_die)])
        else:
            base_die_value = action.n_damage_die * action.damage_die.Roll(False)

    total_damage_per_hit = base_die_value + \
        (0 if action.flat_damage is None else action.flat_damage)
    total_damage = (0 if action.n_hit_rolls is None else action.n_hit_rolls) * \
        total_damage_per_hit

    if sum([vulnerable, immunity, resistance]) > 1:
        raise ValueError("Can only be weak | immune | resistant.")

    if vulnerable:
        rvi_modifier = 2
    elif immunity:
        rvi_modifier = 0
    elif resistance:
        rvi_modifier = 1/2
    else: 
        rvi_modifier = 1

    if action.half_damage_on_fail:
        return (total_damage * hit_probability + (1 - hit_probability) 
                * 1/2 * total_damage) * rvi_modifier
    else:
        return total_damage * hit_probability * rvi_modifier
    

def calculate_hit_economy(action,
                          action_character: Character,
                          scarcity_coeff: float = 0.45,
                          **kwargs):
    if action.action_time == "A":
        time_cost = 1
    elif action.action_time == "B":
        time_cost = 0.5
    elif action.action_time == "R":
        time_cost = 0
    else: 
        time_cost = 2
    
    if hasattr(action, "spell_level"):
        if action.spell_level == 0:
            spell_level = 0
            ss_scarcity_factor = 1
        else:
            total_spellslots = sum([v.n_remaining() for k, v in
                                    action_character.spellslots.items()])
            spell_level = action.spell_level
            level_slots = action_character.spellslots[spell_level].n_remaining()

            ss_scarcity_factor = (total_spellslots/level_slots) ** scarcity_coeff
    else:
        spell_level = 0
        ss_scarcity_factor = 1

    total_cost = (spell_level + time_cost) * ss_scarcity_factor

    if total_cost == 0:
        total_cost = 1

    if action.utility is not None:
        utility_offset = action.utility 
    else: 
        utility_offset = 0

    expected_hit = calculate_expected_hit(action, **kwargs)

    return np.log((expected_hit + utility_offset)/(total_cost ** (1/2)))


def character_driven_interaction(action,
                                 target: Character,
                                 stat: str = "ehit",
                                 override_target_checkval: int = None,
                                 **kwargs):
    if type(action) not in (TurnAction, SpellTurnAction):
        raise ValueError("action must be of type either TurnAction or SpellTurnAction.")
    
    accepted_stats = ['ehit', 'phit', 'econ']
    if stat not in accepted_stats:
        raise ValueError("stat must be one of %s." % accepted_stats)
    
    if stat == 'ehit':
        stat_calc_func = calculate_expected_hit
    elif stat == "phit":
        stat_calc_func = calculate_hit_probability
    else:
        stat_calc_func = calculate_hit_economy

    action_hit_type = action.damage_type
    if action_hit_type is None:
        hit_vuln, hit_resist, hit_immune = False, False, False
    else:
        hit_vuln = target.vulnerablities[action_hit_type]
        hit_resist = target.resistances[action_hit_type]
        hit_immune = target.immunities[action_hit_type]

    if sum([hit_vuln, hit_resist, hit_immune]) > 1:
        raise ValueError("target cannot be vulnerable | resistant | immune simultaneously")

    if action.roll_type in ("hit", "no_roll"):
        if override_target_checkval is None:
            target_ac = target.AC
        else:
            # NonNegativeIntegerCheck(override_target_checkval)
            target_ac = override_target_checkval
        return stat_calc_func(action,
                              vulnerable = hit_vuln,
                              immunity = hit_immune,
                              resistance = hit_resist,
                              opposing_AC = target_ac,
                              **kwargs)
    elif action.roll_type == "save":
        save_type = action.DC_type
        if override_target_checkval is None:
            target_save_value = target.st_modifiers[save_type]
        else:
            # NonNegativeIntegerCheck(override_target_checkval)
            target_save_value = override_target_checkval
        return stat_calc_func(action,
                              vulnerable = hit_vuln,
                              immunity = hit_immune,
                              resistance = hit_resist,
                              opposing_ST = target_save_value,
                              **kwargs)
    

def build_hit_stat_table(target: Character,
                         action_character: Character,
                         stat: str,
                         value_check_min: int = -30,
                         value_check_max: int = 30,
                         **kwargs):
    value_range = range(value_check_min, value_check_max + 1)
    all_actions = action_character.abilities
    stat_table_dict = {}

    for action_name, action_obj in all_actions.items():
        action_outcomes = {val: character_driven_interaction(action = action_obj,
                                                        target = target,
                                                        stat = stat,
                                                        action_character = action_character,
                                                        override_target_checkval=val,
                                                        **kwargs)
                                                        for val in value_range}
        stat_table_dict[action_name] = action_outcomes

    stat_table = pd.DataFrame.from_dict(stat_table_dict)

    return stat_table


def filter_abilities_by_attr(ability_map: dict,
                             attr_name: str,
                             attr_filter: str):
    
    def ability_attr_check(ability, attr_name, attr_filter):
        if type(ability) not in (TurnAction, SpellTurnAction):
            raise ValueError("action must be of type either TurnAction or SpellTurnAction.")
        
        if hasattr(ability, attr_name):
            return getattr(ability, attr_name) == attr_filter
        else:
            return False

    if attr_filter == "all":
        return np.array([True] * len(ability_map))
    else:
        ability_mask = [ability_attr_check(ability, attr_name, attr_filter) 
                        for ability in ability_map.values()]
        return np.array(ability_mask)


def retrieve_table_maxes(stat_table: pd.DataFrame,
                         ability_map: dict,
                         check_value: int,
                         roll_filter: str = "all",
                         action_time_filter: list[str] = ["all"],
                         spell_level_filter = ["all"],
                         damage_type_filter: list[str] = ["all"],
                         n_options: int = 5):
    BadArgumentFromListErrorCheck(passed_value = roll_filter,
                                  accepted_values = DC_types + ['all', 'AC'])
    
    [BadArgumentFromListErrorCheck(passed_value = x,
                                  accepted_values = action_times + ['all'])
        for x in action_time_filter]
    
    [BadArgumentFromListErrorCheck(passed_value = x,
                                  accepted_values = damage_types + ['all'])
        for x in damage_type_filter]

    if type(spell_level_filter) is not list:
        spell_level_filter = [spell_level_filter]
    
    for passed_spell_level_filter in spell_level_filter:
        if passed_spell_level_filter != "all" and type(passed_spell_level_filter) is not int:
            raise ValueError("spell_level_filter must be a non-negative integer or all.")
        elif type(passed_spell_level_filter) is int:
            NonNegativeIntegerCheck(passed_spell_level_filter)
    
    if roll_filter == "AC":
        roll_mask = filter_abilities_by_attr(ability_map = ability_map,
                                             attr_name = "roll_type",
                                             attr_filter = "hit")
    else:
        roll_mask = filter_abilities_by_attr(ability_map = ability_map,
                                             attr_name = "DC_type",
                                             attr_filter = roll_filter)
        
    action_time_masks = [filter_abilities_by_attr(ability_map = ability_map,
                                                attr_name = "action_time",
                                                attr_filter = x) for x in action_time_filter]
    action_time_mask = sum(action_time_masks) > 0
    
    spell_level_masks = [filter_abilities_by_attr(ability_map = ability_map,
                                                attr_name = "spell_level",
                                                attr_filter = x) for x in spell_level_filter]
    spell_level_mask = sum(spell_level_masks) > 0
    
    damage_type_masks = [filter_abilities_by_attr(ability_map = ability_map,
                                                attr_name = "damage_type",
                                                attr_filter = x) for x in damage_type_filter]
    damage_type_mask = sum(damage_type_masks) > 0
    
    final_ability_mask = roll_mask & action_time_mask & spell_level_mask & damage_type_mask
    masked_stat_table = stat_table.loc[check_value, final_ability_mask]

    return masked_stat_table.sort_values()[-n_options:]

    
