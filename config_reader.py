import os

import yaml


class ConfigReader:

    def __init__(self, config_path: str):
        self._config = {}
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                self._config = yaml.safe_load(f)

    @property
    def config(self):
        return self._config
