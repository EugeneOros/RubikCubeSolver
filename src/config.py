import os
import json
from src.constants import ROOT_DIR


class Config:

    def __init__(self):
        self.config_dir = ROOT_DIR
        self.settings_file = os.path.join(self.config_dir, 'settings.json')
        try:
            self.settings = json.loads(open(self.settings_file, 'r').read())
        except FileNotFoundError:
            self.settings = {}

        if not os.path.exists(self.config_dir):
            os.mkdir(self.config_dir)

    def get_setting(self, key, default_value=None):
        if key in self.settings:
            return self.settings[key]
        return default_value

    def set_setting(self, key, value):
        self.settings[key] = value
        with open(self.settings_file, 'w') as settings_file:
            json.dump(self.settings, settings_file)
            settings_file.close()


config = Config()
