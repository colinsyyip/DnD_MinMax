from character import Character
from fixed_names import (character_actionsheet_path, character_detail_path,
                         all_resistances, all_vulnerabilities, all_immunities,
                         all_conditions, damage_types, DC_types, blanked_char_sheet)

from hit_calculations import build_hit_stat_table, retrieve_table_maxes
import io
import json
import os
from support_funcs import load_json_from_path

from flask import Flask, render_template, request, redirect, Response


app = Flask(__name__)
app.selected_character = None
app.target = None
app.target_raw_dict = None
app.tables = {"econ": None, "ehit": None, "phit": None}
app.character_ability_filters = {"roll_type": ['all'],
                                 "spell_level": ['all'],
                                 "action_type": ['all'],
                                 "damage_type": ['all']}


def table_build_check():
    if app.selected_character is not None and app.target is not None:

        for k in app.tables.keys():
            app.tables[k] = build_hit_stat_table(target = app.target,
                                                    stat = k,
                                                    action_character = app.selected_character)
            
        print("Tables created.")
    else:
        app.tables = {"econ": None, "ehit": None, "phit": None}


@app.route("/")
def minmax_formpage():
    action_sheet_files = os.listdir(character_actionsheet_path)
    detail_sheet_files = os.listdir(character_detail_path)
    action_sheets = [x.split(".")[0] for x in action_sheet_files]
    detail_sheets = [x.split(".")[0] for x in detail_sheet_files]
    doubly_available_sheets = [x for x in action_sheets if x in detail_sheets]

    total_immunity_options = all_immunities + all_conditions

    action_times_list = ["Action", "Bonus Action", "Reaction", "Longer than 1T"]

    if app.selected_character is None:
        spell_levels = []
        character_stats = {"AC": "-",
                           "MaxHP": "-",
                           "Prof.": "-",
                           "STR": "-",
                           "DEX": "-",
                           "CON": "-",
                           "INT": "-",
                           "WIS": "-",
                           "CHA": "-"}
    else:
        spell_levels = [0] + list(app.selected_character.spellslots.keys()) 
        st_mods = app.selected_character.ability_modifiers
        character_stats = {"AC": "%s" % (app.selected_character.AC),
                           "MaxHP": "%s"% (app.selected_character.MaxHP),
                           "Prof.": "%s" % app.selected_character.Prof_Bonus,
                           "STR": "%s (%s)" % (app.selected_character.STR,
                                             "+%s" % st_mods['STR'] if st_mods['STR'] >= 0 else st_mods['STR']),
                           "DEX": "%s (%s)" % (app.selected_character.DEX,
                                             "+%s" % st_mods['DEX'] if st_mods['DEX'] >= 0 else st_mods['DEX']),
                           "CON": "%s (%s)" % (app.selected_character.CON,
                                             "+%s" % st_mods['CON'] if st_mods['CON'] >= 0 else st_mods['CON']),
                           "INT": "%s (%s)" % (app.selected_character.INT,
                                             "+%s" % st_mods['INT'] if st_mods['INT'] >= 0 else st_mods['INT']),
                           "WIS": "%s (%s)" % (app.selected_character.WIS,
                                             "+%s" % st_mods['WIS'] if st_mods['WIS'] >= 0 else st_mods['WIS']),
                           "CHA": "%s (%s)" % (app.selected_character.CHA,
                                             "+%s" % st_mods['CHA'] if st_mods['CHA'] >= 0 else st_mods['CHA']),}

    table_build_check()
    return render_template("minmax_ui.html",
                           available_characters = doubly_available_sheets,
                           available_resists = all_resistances,
                           available_vulnerabilities = all_vulnerabilities,
                           availabe_immunities = total_immunity_options,
                           char_stats = character_stats,
                           all_roll_types = ['AC'] + DC_types,
                           all_spell_levels = spell_levels,
                           all_action_types = action_times_list,
                           all_damage_types = damage_types,
                           target_form_fill = target_form_fill,
                           ability_filter_form_fill = ability_filter_form_fill,
                           character_select_form_fill = character_select_form_fill)


@app.route("/load_character_sheet", methods=["POST"])
def load_character_sheet():
    char_sheet_select_data = request.form
    chosen_character = char_sheet_select_data.get("chosen_char_sheet")
    character_json = load_json_from_path(chosen_character)
    app.selected_character = Character(**character_json)
    character_action_filepath = "%s/%s.csv" % (character_actionsheet_path,
                                           chosen_character)
    app.selected_character.add_abilities_from_csv(character_action_filepath)
    st_mods = app.selected_character.ability_modifiers
    character_stats = {"AC": "%s" % (app.selected_character.AC),
                        "MaxHP": "%s"% (app.selected_character.MaxHP),
                        "Prof.": "%s" % app.selected_character.Prof_Bonus,
                        "STR": "%s (%s)" % (app.selected_character.STR,
                                            "+%s" % st_mods['STR'] if st_mods['STR'] >= 0 else st_mods['STR']),
                        "DEX": "%s (%s)" % (app.selected_character.DEX,
                                            "+%s" % st_mods['DEX'] if st_mods['DEX'] >= 0 else st_mods['DEX']),
                        "CON": "%s (%s)" % (app.selected_character.CON,
                                            "+%s" % st_mods['CON'] if st_mods['CON'] >= 0 else st_mods['CON']),
                        "INT": "%s (%s)" % (app.selected_character.INT,
                                            "+%s" % st_mods['INT'] if st_mods['INT'] >= 0 else st_mods['INT']),
                        "WIS": "%s (%s)" % (app.selected_character.WIS,
                                            "+%s" % st_mods['WIS'] if st_mods['WIS'] >= 0 else st_mods['WIS']),
                        "CHA": "%s (%s)" % (app.selected_character.CHA,
                                            "+%s" % st_mods['CHA'] if st_mods['CHA'] >= 0 else st_mods['CHA']),}

    table_build_check()
    return character_stats


@app.route("/input_target_stats", methods=['POST'])
def input_target_stats():
    target_stat_form_data = request.form
    target_info_dict = {
        "name": "target",
        "strength": int(target_stat_form_data.get("target_STR")),
        "dexterity": int(target_stat_form_data.get("target_DEX")),
        "constitution": int(target_stat_form_data.get("target_CON")),
        "intelligence": int(target_stat_form_data.get("target_INT")),
        "wisdom": int(target_stat_form_data.get("target_WIS")), 
        "charisma": int(target_stat_form_data.get("target_CHA")),
        "hp": int(target_stat_form_data.get("target_HP")),
        "proficiency_bonus": int(target_stat_form_data.get("target_prof")),
        "ac": int(target_stat_form_data.get("target_AC")),
    }

    if app.target_raw_dict is None:
        app.target_raw_dict = target_info_dict
    else:
        app.target_raw_dict.update(target_info_dict)
    app.target = Character(**target_info_dict)

    table_build_check()
    return redirect("/")


@app.route("/input_target_st_prof", methods=['POST'])
def input_target_st_prof():
    # Add in logic here to check that we have basic target stats first
    target_st_proff_form_data = request.form
    form_keys = list(target_st_proff_form_data.keys())
    st_profs = [x.strip("st_") for x in form_keys if x[:3] == "st_"]
    target_st_info_dict = {
        "st_proficiencies": st_profs
    }

    app.target_raw_dict.update(target_st_info_dict)
    app.target = Character(**app.target_raw_dict)

    table_build_check()
    return redirect("/")


@app.route("/input_target_rvi", methods=['POST'])
def input_target_rvi():
    target_rvi_form_data = request.form

    known_key_map = {'target_resist': 'resistances', 
                     'target_vuln': 'vulnerabilities', 
                     'target_immune': 'immunities'}
    
    target_rvi_dict = {}

    for key, remapped_key in known_key_map.items(): 
        values = target_rvi_form_data.getlist(key)
        if "None" in values and len(values) > 1:
            values.pop(values.index("None"))
        target_rvi_dict[remapped_key] = values

    app.target_raw_dict.update(target_rvi_dict)
    app.target = Character(**app.target_raw_dict)

    table_build_check()
    return redirect("/")


def target_form_fill(variable, rvi_type: str = None):
    if app.target is None:
        return ""
    else:
        if variable[:3] == "st_":
            saving_throw_type = variable.strip("st_")
            if app.target.st_proficiencies[saving_throw_type]:
                return 'checked'
            else:
                return ''
        elif "rvi" in variable and rvi_type is not None:
            if "resist" in variable:
                rvi_lookup_dict = app.target.resistances
            elif "vulnerability" in variable:
                rvi_lookup_dict = app.target.vulnerablities
            else:
                rvi_lookup_dict = app.target.immunities
            
            if rvi_lookup_dict[rvi_type]:
                return 'selected'
            else:
                return ''
        else:
            try:
                return getattr(app.target, variable)
            except AttributeError:
                return ''
            

def character_select_form_fill(char_name):
    if app.selected_character is None and char_name == "placeholder":
        return 'selected'
    elif app.selected_character is not None and app.selected_character.name.lower() == char_name.lower():
        return 'selected'
    else:
        return ''
            

def ability_filter_form_fill(filter_type, filter_value):
    check_list = app.character_ability_filters[filter_type]
    if filter_type == "action_type":
        filter_value = filter_value[0]
    if filter_value in check_list:
        return 'selected'
    else:
        return ''
    

@app.route("/spell_filter_options_refresh", methods=['POST', 'GET'])
def spell_filter_options_refresh():
    spell_levels = [0] + list(app.selected_character.spellslots.keys())
    return render_template('spell_filter_options.html',
                           all_spell_levels=spell_levels,
                           ability_filter_form_fill=ability_filter_form_fill)
            

@app.route("/hit_tables_fill", methods=['POST', 'GET'])
def hit_tables_fill():
    hit_max_tuples = {"phit": None,
                      "ehit": None,
                      "econ": None}
    if all([x is None for x in app.tables.values()]):
        dummy_dict = {x: [] for x in ['AC'] + DC_types}
        print("No tables found...")
        return render_template('hit_table_row_divs.html', 
                               all_roll_types = ["AC"] + DC_types,
                               phit_items=dummy_dict,
                               ehit_items=dummy_dict,
                               econ_items=dummy_dict)
    else:
        print("Calculating maxes...")
        for stat, calc_table in app.tables.items():
            hit_max_tuple_sub_dict = {}
            for roll_filter in DC_types + ["AC"]:
                if roll_filter == "AC":
                    check_value = app.target.AC
                else:
                    check_value = app.target.st_modifiers[roll_filter]
                table_maxes = retrieve_table_maxes(calc_table,
                                                app.selected_character.abilities,
                                                check_value = check_value,
                                                roll_filter = roll_filter,
                                                action_time_filter = app.character_ability_filters['action_type'],
                                                spell_level_filter = app.character_ability_filters['spell_level'],
                                                damage_type_filter = app.character_ability_filters['damage_type'],
                                                n_options=3).sort_values(ascending=False)
                table_max_tuples = [(v, k) for k, v in table_maxes.to_dict().items()]
                if stat == 'phit':
                    table_max_tuples = [("%.0f%%" % (x[0] * 100), x[1]) for x in table_max_tuples]
                else:
                    table_max_tuples = [("%.1f" % x[0], x[1]) for x in table_max_tuples]
            
                hit_max_tuple_sub_dict[roll_filter] = table_max_tuples
            
            hit_max_tuples[stat] = hit_max_tuple_sub_dict

        return render_template('hit_table_row_divs.html', 
                               all_roll_types = ["AC"] + DC_types,
                               phit_items=hit_max_tuples['phit'],
                               ehit_items=hit_max_tuples['ehit'],
                               econ_items=hit_max_tuples['econ'])


@app.route("/target_clear")
def target_clear():
    app.target = None
    app.target_raw_dict = None
    app.tables = {"econ": None, "ehit": None, "phit": None}
    return redirect("/")


@app.route("/input_ability_filters", methods=['POST'])
def input_ability_filters():
    ability_filters_formdata = request.form

    filter_keys = ['roll_type', 'spell_level',
                   'action_type', 'damage_type']
    
    action_filter_dict = {}
    
    for filter_key in filter_keys:
        filter_value = ability_filters_formdata.getlist(filter_key)

        if "all" in filter_value and len(filter_value) > 1:
            filter_value.pop(filter_value.index("all"))

        if filter_key == "action_type" and "all" not in filter_value:
            filter_value = [x[0] for x in filter_value]

        if filter_key == "spell_level" and "all" not in filter_value:
            filter_value = [int(x) for x in filter_value]

        action_filter_dict[filter_key] = filter_value
    
    app.character_ability_filters.update(action_filter_dict)

    return redirect("/")


def retrieve_character_list():
    character_sheets = os.listdir(character_detail_path)
    if ".DS_Store" in character_sheets:
        character_sheets.pop(character_sheets.index(".DS_Store"))
    character_sheets = [x.strip(".json") for x in character_sheets]

    return character_sheets


@app.route("/modify_sheets")
def modify_character_sheets():
    return render_template("config_edit.html",
                           available_characters = sorted(retrieve_character_list()))


@app.route("/input_character_json_select", methods=['POST'])
def input_character_json_select():
    form_data = request.form
    chosen_char = form_data.get('chosen_char_sheet')
    chosen_char_json = load_json_from_path(chosen_char)

    return json.dumps(chosen_char_json)


@app.route("/save_character_json_input", methods=['POST'])
def save_character_json_input():
    passed_args = request.get_json()
    raw_text_value = passed_args['text_area']
    parsed_text_value_dict = json.loads(raw_text_value)
    editing_character = passed_args['editing_character']

    f_path = "%s/%s_TEST.json" % (character_detail_path, editing_character.lower())
    with open(f_path, 'w') as wf:
        json.dump(parsed_text_value_dict, wf)

    return render_template('char_select_options.html',
                           available_characters = sorted(retrieve_character_list()))


@app.route("/new_character_json_input", methods=['POST'])
def new_character_json_input():
    return blanked_char_sheet

if __name__ == "__main__":
    app.run(port=8080, debug = True)