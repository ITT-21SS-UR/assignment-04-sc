import math
import sys
from datetime import datetime
from enum import Enum

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
    TARGET_POSITIONS = "target_positions"
    TOTAL_RUNS = "total_runs"

    # remaining csv column names
    CONDITION = "condition"
    POINTER_TYPE = "pointer_type"
    MOUSE_START_POSITION_X = "mouse_start_x_position"
    MOUSE_START_POSITION_Y = "mouse_start_y_position"
    MOUSE_CLICKED_POSITION_X = "mouse_clicked_x_position"
    MOUSE_CLICKED_POSITION_Y = "mouse_clicked_y_position"
    DISTANCE_TO_START_POSITION = "distance_to_start_position"

    CIRCLE_CLICKED = "is_circle_clicked"
    IS_TARGET = "is_target"

    TASK_COMPLETION_TIME = "task_completion_time_in_ms"
    TIMESTAMP = "timestamp"
    ROUND = "round"

    # remaining constants
    INVALID_TIME = "NaN"

    @staticmethod
    def __write_to_stdout_in_csv_format(row_data):
        row_data_values = list(row_data.values())
        values_length = len(row_data_values)

        for i in range(values_length):
            value = str(row_data_values[i])

            if i == values_length - 1:
                sys.stdout.write(value)
            else:
                sys.stdout.write(value + ",")

        sys.stdout.write("\n")
        sys.stdout.flush()

    def __init__(self, config):
        super().__init__()

        self.config = config

        self.__reset_model()
        self.__stdout_csv_column_names()

    def __reset_model(self):
        self.__round = 0
        self.__pointer_type = Pointer.NORMAL_POINTER  # TODO

        self.__mouse_start_position = QtCore.QPoint(0, 0)  # TODO start position

        self.__condition = Condition.CONDITION_1

        self.__start_time = self.INVALID_TIME
        self.__end_time = self.INVALID_TIME

    def __get_csv_columns(self):
        return [
            self.PARTICIPANT_ID,
            self.CONDITION,
            self.POINTER_TYPE,
            self.MOUSE_START_POSITION_X,
            self.MOUSE_START_POSITION_Y,
            self.MOUSE_CLICKED_POSITION_X,
            self.MOUSE_CLICKED_POSITION_Y,
            self.DISTANCE_TO_START_POSITION,
            self.CIRCLE_COUNT,
            self.CIRCLE_CLICKED,
            self.IS_TARGET,
            self.TASK_COMPLETION_TIME,
            self.TIMESTAMP,
            self.ROUND
        ]

    def __stdout_csv_column_names(self):
        for column_name in self.__get_csv_columns():
            if column_name == self.__get_csv_columns()[-1]:
                sys.stdout.write(str(column_name))
            else:
                sys.stdout.write(str(column_name) + ",")

        sys.stdout.write("\n")
        sys.stdout.flush()

    def __calculate_distance_to_start_position(self, mouse_position):
        return math.hypot(
            mouse_position.x() - self.__mouse_start_position.x(),
            mouse_position.y() - self.__mouse_start_position.y()
        )

    def __calculate_task_time(self):
        try:
            return (self.__end_time - self.__start_time).total_seconds() * 1000
        except AttributeError:
            return self.INVALID_TIME
        except TypeError:
            return self.INVALID_TIME

    def __create_row_data(self, mouse_position, circle_clicked=False, is_target=False):
        return {
            self.PARTICIPANT_ID: self.config[self.PARTICIPANT_ID],
            self.CONDITION: self.__condition.value,
            self.POINTER_TYPE: self.__pointer_type.value,
            self.MOUSE_START_POSITION_X: self.__mouse_start_position.x(),
            self.MOUSE_START_POSITION_Y: self.__mouse_start_position.y(),
            self.MOUSE_CLICKED_POSITION_X: mouse_position.x(),
            self.MOUSE_CLICKED_POSITION_Y: mouse_position.y(),
            self.DISTANCE_TO_START_POSITION: self.__calculate_distance_to_start_position(mouse_position),
            self.CIRCLE_COUNT: self.config[self.CIRCLE_COUNT],
            self.CIRCLE_CLICKED: circle_clicked,
            self.IS_TARGET: is_target,
            self.TASK_COMPLETION_TIME: self.__calculate_task_time(),
            self.TIMESTAMP: datetime.now(),
            self.ROUND: self.__round
        }

    def handle_false_clicked(self, mouse_position):
        self.__write_to_stdout_in_csv_format(self.__create_row_data(mouse_position))

    def handle_circle_clicked(self, mouse_position, is_target):
        if is_target:
            self.__round += 1  # TODO sth with round
            self.__end_time = datetime.now()
            self.__write_to_stdout_in_csv_format(
                self.__create_row_data(mouse_position, circle_clicked=True, is_target=is_target))

            self.__start_time = self.INVALID_TIME
            self.__end_time = self.INVALID_TIME

        else:
            self.__end_time = self.INVALID_TIME
            self.__write_to_stdout_in_csv_format(self.__create_row_data(mouse_position, circle_clicked=True))

    def start_timer(self):
        if self.__start_time == self.INVALID_TIME:
            self.__start_time = datetime.now()
