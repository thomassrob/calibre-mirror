import os

import yaml


class ConfigReader:

    def __init__(self, config_path: str):
        self._configs = []
        if os.path.exists(config_path):
            try:
                with open(config_path, "r") as f:
                    for config in yaml.safe_load_all(f):
                        print(config)
                        self._configs.append(config)
            except yaml.YAMLError as e:
                error_msg = f"Error parsing YAML file '{config_path}': {str(e)}"
                problem_mark = getattr(e, 'problem_mark', None)
                if problem_mark is not None:
                    error_msg += f"\nError at line {problem_mark.line + 1}, column {problem_mark.column + 1}"
                raise ValueError(error_msg) from e
            except Exception as e:
                error_msg = f"Unexpected error reading YAML file '{config_path}': {str(e)}"
                raise ValueError(error_msg) from e

    @property
    def configs(self):
        return self._configs
