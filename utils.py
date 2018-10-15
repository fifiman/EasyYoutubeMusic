import json
import os

def create_directory(dir_path):
	if not os.path.exists(os.path.dirname(dir_path)):
	    try:
	        os.makedirs(os.path.dirname(dir_path))
	    except OSError as exc: # Guard against race condition
	        if exc.errno != errno.EEXIST:
	            raise

def pretty_print_json(json_text):
	print(json.dumps(json_text, indent=2))