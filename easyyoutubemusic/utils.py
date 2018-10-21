import json
import os

def pretty_print_json(json_text):
	print(json.dumps(json_text, indent=2))