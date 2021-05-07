import math
import os
from datetime import datetime
from enum import Enum

import pandas as pd
from PyQt5 import QtCore
from PyQt5.QtCore import QObject


class State(Enum):
    DESCRIPTION_STUDY = 1
    NORMAL_POINTER = 2
    NOVEL_POINTER = 3
    DESCRIPTION_END = 4


class Condition(Enum):
    # TODO conditions should probably be different
    # how many condition do we want to have 3?
    CONDITION_1 = "condition1"
    CONDITION_2 = "condition2"
    CONDITION_3 = "condition3"


class Pointer(Enum):
    NORMAL_POINTER = "normal pointer"
    NOVEL_POINTER = "novel pointer"


class PointingExperimentModel(QObject):
    # relevant dict keys of ini and json file
    PARTICIPANT_ID = "participant_id"
    COLOR_BACKGROUND = "color_background"
    COLOR_CIRCLES = "color_circles"
    COLOR_TARGET = "color_target"
    CIRCLE_MIN_SIZE = "circle_min_size"
    CIRCLE_MAX_SIZE = "circle_max_size"
    CIRCLE_COUNT = "circle_count"
    MAX_REPETITIONS = "max_repetitions"
    TOTAL_RUNS = "total_runs"

    # remaining csv column names
    CONDITION = "condition"
    MOUSE_START_POSITION_X = "mouse_start_x_position"
    MOUSE_START_POSITION_Y = "mouse_start_y_position"
    MOUSE_CLICKED_POSITION_X = "mouse_clicked_x_position"
    MOUSE_CLICKED_POSITION_Y = "mouse_clicked_y_position"
    DISTANCE_TO_START_POSITION = "distance_to_start_position"

    CIRCLE_CLICKED = "is_circle_clicked"
    IS_TARGET = "is_correct_target"

    REACTION_TIME = "reaction_time_in_ms"
    TASK_COMPLETION_TIME = "task_completion_time"  # TODO when should it be started and logged
    TIMESTAMP = "timestamp"

    # remaining constants
    INVALID_TIME = "NaN"

    def __init__(self, config):
        super().__init__()

        self.config = config

        self.__create_log_directory()
        self.__reset_model()

    def __create_log_directory(self):
        self.__log_directory = "raw_log_data"

        if not os.path.isdir(self.__log_directory):
            os.makedirs(self.__log_directory)

    def __reset_model(self):
        self.__mouse_start_position = QtCore.QPoint(0, 0)  # TODO start position

        self.__set_condition(Condition.CONDITION_1)

        self.__start_time = datetime.now()  # TODO when it is relevant update the start time self.INVALID_TIME
        self.__end_time = self.INVALID_TIME

    def __set_condition(self, condition):
        self.__condition = condition
        self.__update_file()

    def __update_file(self):
        self.__file = "./" + self.__log_directory + "/id_" + str(self.config[self.PARTICIPANT_ID]) \
                      + "_trial_" + self.__condition.value \
                      + ".csv"

    def __calculate_distance_to_start_position(self, mouse_position):
        # https://stackoverflow.com/questions/5228383/how-do-i-find-the-distance-between-two-points
        return math.hypot(
            mouse_position.x() - self.__mouse_start_position.x(),
            mouse_position.y() - self.__mouse_start_position.y()
        )

    def __calculate_reaction_time(self):
        self.__end_time = datetime.now()  # TODO at another place

        try:
            return (self.__end_time - self.__start_time).total_seconds() * 1000
        except AttributeError:
            return self.INVALID_TIME
        except TypeError:
            return self.INVALID_TIME

    def __create_row_data(self, mouse_position, circle_clicked=False, is_target=False):
        # TODO only use default values when necessary; some are only tmp
        return {
            self.PARTICIPANT_ID: self.config[self.PARTICIPANT_ID],
            self.CONDITION: self.__condition.value,
            self.MOUSE_START_POSITION_X: self.__mouse_start_position.x(),
            self.MOUSE_START_POSITION_Y: self.__mouse_start_position.y(),
            self.MOUSE_CLICKED_POSITION_X: mouse_position.x(),
            self.MOUSE_CLICKED_POSITION_Y: mouse_position.y(),
            self.DISTANCE_TO_START_POSITION: self.__calculate_distance_to_start_position(mouse_position),
            self.CIRCLE_COUNT: self.config[self.CIRCLE_COUNT],
            self.CIRCLE_CLICKED: circle_clicked,
            self.IS_TARGET: is_target,
            self.REACTION_TIME: self.__calculate_reaction_time(),
            # self.TASK_COMPLETION_TIME,  # TODO when should it be started and logged
            self.TIMESTAMP: datetime.now()
        }

    def __write_to_csv(self, row_data):
        # TODO The script outputs all necessary information on stdout in CSV format
        if os.path.isfile(self.__file):
            data_frame = pd.read_csv(self.__file)
        else:
            data_frame = pd.DataFrame(columns=[
                self.PARTICIPANT_ID,
                self.CONDITION,
                self.MOUSE_START_POSITION_X,
                self.MOUSE_START_POSITION_Y,
                self.MOUSE_CLICKED_POSITION_X,
                self.MOUSE_CLICKED_POSITION_Y,
                self.DISTANCE_TO_START_POSITION,
                self.CIRCLE_COUNT,
                self.CIRCLE_CLICKED,
                self.IS_TARGET,
                self.REACTION_TIME,
                # self.TASK_COMPLETION_TIME,  # TODO when should it be started and logged
                self.TIMESTAMP
            ])

        data_frame = data_frame.append(row_data, ignore_index=True)
        data_frame.to_csv(self.__file, index=False)

    def handle_false_clicked(self, mouse_position):
        self.__write_to_csv(self.__create_row_data(mouse_position))

    def handle_circle_clicked(self, mouse_position):
        is_target = False  # TODO check if it is the target
        self.__write_to_csv(self.__create_row_data(mouse_position, circle_clicked=True, is_target=is_target))
