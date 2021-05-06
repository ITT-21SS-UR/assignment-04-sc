import configparser
import json
import os
import sys
from enum import Enum

import pandas as pd
from PyQt5.QtCore import QObject


class State(Enum):
    DESCRIPTION_STUDY = 1
    NORMAL_POINTER = 2
    NOVEL_POINTER = 3
    DESCRIPTION_END = 4


class Condition(Enum):
    # TODO conditions should probably be different
    # how many condition do we want to have 3?
    NORMAL_POINTER = "normal pointer"
    NOVEL_POINTER = "novel pointer"


class PointingExperimentModel(QObject):
    # relevant dict keys for ini and json file
    PARTICIPANT_ID = "participant_id"
    COLOR_BACKGROUND = "color_background"
    COLOR_CIRCLES = "color_circles"
    COLOR_TARGET = "color_target"
    CIRCLE_MIN_SIZE = "circle_min_size"
    CIRCLE_MAX_SIZE = "circle_max_size"
    CIRCLE_COUNT = "circle_count"
    MAX_REPETITIONS = "max_repetitions"
    TOTAL_RUNS = "total_runs"

    def __init__(self, test_config):
        super().__init__()

        self.test_config = test_config

    def __write_to_csv(self, row_data):
        try:
            data_frame = pd.read_csv(self.__file)
        except FileNotFoundError:
            data_frame = pd.DataFrame(columns=[
                # self.PARTICIPANT_ID,
                # self.CONDITION,
                # self.SHOWN_STIMULUS,
                # self.REACTION_TIME,
                # self.TIMESTAMP,
                # self.CORRECT_CIRCLE
            ])

        data_frame = data_frame.append(row_data, ignore_index=True)
        data_frame.to_csv(self.__file, index=False)


def exit_program(message="Please give a valid .ini or .json file as arguments (-_-)\n"):
    sys.stderr.write(message)
    sys.exit(1)


def create_ini_config(file_name):
    config = configparser.ConfigParser()
    config.read(file_name)

    return dict(config["DEFAULT"])


def create_json_config(file_name):
    with open(file_name) as file:
        return json.load(file)


def read_test_config():
    if len(sys.argv) < 2:
        exit_program()

    file_name = sys.argv[1]

    if not os.path.isfile(file_name):
        exit_program("File does not exist (-_-)\n")

    file_extension = os.path.splitext(file_name)

    if file_extension[-1] == ".ini":
        return create_ini_config(file_name)

    elif file_extension[-1] == ".json":
        return create_json_config(file_name)

    else:
        exit_program()


if __name__ == '__main__':
    test_config = read_test_config()  # TODO move to pointing experiment
    # TODO check if file contains correct and all relevant data?

    model = PointingExperimentModel(test_config)
