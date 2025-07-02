import requests
import json
from utils.read_write import read_json_file
from utils.safe_update_dict import safe_update_dict

# Test read_json_file (will trigger error)
read_json_file("file.json")

# Test safe_update_dict (will trigger warnings)
dict1 = {"a": 1, "b": "2", "c": {"d": {"x": 1, "y": 2}, "e": 4}}
dict2 = {"b": 20, "c": {"d": 30, "f": 5}, "new_key": "new_value"}

safe_update_dict(dict1, dict2)
print("Updated dict1:", dict1)





