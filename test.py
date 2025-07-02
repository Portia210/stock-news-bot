import requests
import json
from utils.read_write import read_json_file
from utils.safe_update_dict import safe_update_dict

# Test read_json_file (will trigger error)
read_json_file("file.json")

