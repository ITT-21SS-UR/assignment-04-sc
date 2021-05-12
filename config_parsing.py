import ast
import configparser
import json
import os
import sys

from pointing_experiment_model import ConfigKeys


# Author: Claudia
# Author of all test_config files: Claudia
class ConfigParsing:
    @staticmethod
    def __exit_program(message="Please give a valid .ini or .json file as argument (-_-)\n"):
        sys.stderr.write(message)
        sys.exit(1)

    def __init__(self):
        self.__config = self.__read_test_config()
        self.__exit_if_not_valid_config()

    def __create_ini_config(self):
        config = configparser.ConfigParser()
        config.read(self.file_name)

        ini_dict = dict(config["DEFAULT"])

        target_position_key = ConfigKeys.TARGET_POSITIONS.value
        ini_dict[target_position_key] = ast.literal_eval((ini_dict[target_position_key]))

        conditions_key = ConfigKeys.CONDITIONS.value
        ini_dict[conditions_key] = ast.literal_eval((ini_dict[conditions_key]))

        return ini_dict

    def __create_json_config(self):
        with open(self.file_name) as file:
            return json.load(file)

    def __read_test_config(self):
        if len(sys.argv) < 2:
            self.__exit_program()

        self.file_name = sys.argv[1]

        if not os.path.isfile(self.file_name):
            self.__exit_program("File does not exist (-_-)\n")

        file_extension = os.path.splitext(self.file_name)

        if file_extension[-1] == ".ini":
            return self.__create_ini_config()

        elif file_extension[-1] == ".json":
            return self.__create_json_config()

        else:
            self.__exit_program()

    def __exit_if_not_valid_config(self):
        missing_key = False

        for key in ConfigKeys.get_all_values():

            if key not in self.__config:
                # sub elements of config file are not checked
                if key != ConfigKeys.CIRCLE_SIZE.value \
                        and key != ConfigKeys.CIRCLE_COUNT.value \
                        and key != ConfigKeys.DISTRACTION.value:
                    missing_key = True
                    print("config: no {0} found".format(key))

        if missing_key:
            self.__exit_program()

    def get_config(self):
        return self.__config
