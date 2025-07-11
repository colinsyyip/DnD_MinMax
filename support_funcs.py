from fixed_names import character_actionsheet_path, character_detail_path
import json
import pandas as pd

def load_json_from_path(file_name, json_file_path: str = character_detail_path):
    with open("%s/%s.json" % (json_file_path, file_name), "r") as f:
        json_file = f.read()
        f.close()
    json_to_dict = json.loads(json_file)

    return json_to_dict

def load_csv_from_path(csv_file_path: str = character_actionsheet_path):
    return pd.read_csv(csv_file_path)