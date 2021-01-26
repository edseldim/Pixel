import json
import os
import time
settings = None
dir_path = os.path.dirname(os.path.realpath('python_bot.py'))
with open(f"{dir_path}/misc_settings.json") as f:
    settings = json.load(f)
settings['local_day'] = time.localtime().tm_mday
with open(f"{dir_path}/misc_settings.json", 'w') as write_file:
    json.dump(settings, write_file)
