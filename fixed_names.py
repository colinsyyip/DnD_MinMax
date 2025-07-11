damage_types = ['Acid', 'Cold', 'Fire', 'Force', 'Lightning',
                'Necrotic', 'Poison', 'Psychic', 'Radiant', 'Thunder',
                'Bludgeoning', 'Piercing', 'Slashing', 'No Damage']

DC_types = ['STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA']

full_stat_names = ["Strength", "Dexterity", "Constitution",
                   "Intelligence", "Wisdom", "Charisma"]

roll_types = ['hit', 'save', 'no_roll']

action_times = ["A", "B", "R", "L"]

all_proficiencies = ['Acrobatics', 'Animal Handling', 'Arcana',
                 'Athletics', 'Deception', 'History',
                 'Insight', 'Intimidation', 'Investigation',
                 'Medicine', 'Nature' ,'Perception', 
                 'Performance', 'Persuasion', 'Religion',
                 'Sleight of Hand', 'Stealth', 'Survival']

all_resistances = ["Acid", "Bludgeoning", "Bludgeoning (M)", 
                   "Bludgeoning (NM)", "Cold", "Damage (Trap)", 
                   "Damage (Spells)", "Damage (Breath)", "Fire", 
                   "Force", "Lightning", "Necrotic", "Piercing",
                   "Piercing (NM)", "Poison", "Psychic", 
                   "Radiant", "Ranged Attacks", "Slashing", 
                   "Slashing (M)", "Thunder"]

all_vulnerabilities = ['Acid', 'Cold', 'Fire', 'Force', 'Lightning',
                       'Necrotic', 'Poison', 'Psychic', 'Radiant', 
                       'Thunder', 'Bludgeoning', 'Piercing', 'Slashing']

all_immunities = ['Acid', 'Cold', 'Fire', 'Force', 'Lightning',
                  'Necrotic', 'Poison', 'Psychic', 'Radiant',
                  'Thunder', 'Bludgeoning', 'Piercing', 'Slashing',
                  'Bludgeoning (NM)']

all_conditions = ['Blinded', 'Charmed', 'Deafened', 'Exhaustion',
                  'Frightened', 'Grappled', 'Incapacitated',
                  'Invisible', 'Paralyzed', 'Petrified', 
                  'Poisoned', 'Prone', 'Restrained', 'Stunned',
                  'Unconscious']

character_actionsheet_path = "character_actionsheets/"

character_detail_path = "character_details/"

blanked_char_sheet = {
    "name": "",
    "strength": 0,
    "dexterity": 0,
    "constitution": 0,
    "intelligence": 0,
    "wisdom": 0,
    "charisma": 0,
    "hp": 0,
    "proficiency_bonus": 0,
    "ac": 0,
    "st_proficiencies": [],
    "half_proficiencies": [],
    "proficiencies": [],
    "expertise": [],
    "resistances": [],
    "immunities": [],
    "spell_slots": {}
}