import os

import yaml


class ConfigReader:

    def __init__(self, config_path: str):
        self._configs = []
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                for config in yaml.safe_load_all(f):
                    print(config)
                    self._configs.append(config)

    @property
    def configs(self):
        return self._configs
