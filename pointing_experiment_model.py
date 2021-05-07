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
