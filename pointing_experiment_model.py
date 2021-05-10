import math
import random
import sys
from datetime import datetime
from enum import Enum

from PyQt5.QtCore import QObject


class Pointer(Enum):
    NORMAL_POINTER = "normal"
    NOVEL_POINTER = "novel"


class ConfigKeys(Enum):
    PARTICIPANT_ID = "participant_id"
    POINTER_TYPE = "pointer_type"
    COLOR_BACKGROUND = "color_background"
    COLOR_CIRCLES = "color_circles"
    COLOR_TARGET = "color_target"
    CIRCLE_SIZE = "circle_size"
    CIRCLE_COUNT = "circle_count"
    DISTRACTION = "distraction"
    CONDITIONS = "conditions"
    TARGET_POSITIONS = "target_positions"

    @staticmethod
    def get_all_values():
        return list(map(lambda v: v.value, ConfigKeys))


class PointingExperimentModel(QObject):
    # remaining csv column names
    CONDITION = "condition"
    MOUSE_START_POSITION_X = "mouse_start_x_position"
    MOUSE_START_POSITION_Y = "mouse_start_y_position"
    MOUSE_CLICKED_POSITION_X = "mouse_clicked_x_position"
    MOUSE_CLICKED_POSITION_Y = "mouse_clicked_y_position"
    DISTANCE_TO_START_POSITION = "distance_to_start_position"

    CIRCLE_CLICKED = "is_circle_clicked"
    IS_TARGET = "is_target"

    TASK_COMPLETION_TIME = "task_completion_time_in_ms"
    TIMESTAMP = "timestamp"

    # remaining constant
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

        conditions = self.config[ConfigKeys.CONDITIONS.value]

        self.__condition = conditions[0]
        self.__target_positions = []
        self.__target_position_index = 0

        self.__start_time = self.INVALID_TIME
        self.__end_time = self.INVALID_TIME

        self.__setup_target_positions()
        self.__stdout_csv_column_names()

    def __setup_target_positions(self):
        self.__target_positions = self.config[ConfigKeys.TARGET_POSITIONS.value]
        random.shuffle(self.__target_positions)

    def __get_csv_columns(self):
        return [
            ConfigKeys.PARTICIPANT_ID.value,
            self.CONDITION,
            ConfigKeys.POINTER_TYPE.value,
            self.MOUSE_START_POSITION_X,
            self.MOUSE_START_POSITION_Y,
            self.MOUSE_CLICKED_POSITION_X,
            self.MOUSE_CLICKED_POSITION_Y,
            self.DISTANCE_TO_START_POSITION,
            ConfigKeys.CIRCLE_COUNT.value,
            ConfigKeys.CIRCLE_SIZE.value,
            self.CIRCLE_CLICKED,
            self.IS_TARGET,
            self.TASK_COMPLETION_TIME,
            self.TIMESTAMP
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
            ConfigKeys.PARTICIPANT_ID.value: self.get_participant_id(),
            self.CONDITION: self.__condition["id"],
            ConfigKeys.POINTER_TYPE: self.get_pointer(),
            self.MOUSE_START_POSITION_X: self.__mouse_start_position.x(),
            self.MOUSE_START_POSITION_Y: self.__mouse_start_position.y(),
            self.MOUSE_CLICKED_POSITION_X: mouse_position.x(),
            self.MOUSE_CLICKED_POSITION_Y: mouse_position.y(),
            self.DISTANCE_TO_START_POSITION: self.__calculate_distance_to_start_position(mouse_position),
            ConfigKeys.CIRCLE_COUNT: self.get_circle_count(),
            ConfigKeys.CIRCLE_SIZE: self.get_circle_size(),
            self.CIRCLE_CLICKED: circle_clicked,
            self.IS_TARGET: is_target,
            self.TASK_COMPLETION_TIME: self.__calculate_task_time(),
            self.TIMESTAMP: datetime.now()
        }

    def set_mouse_start_position(self, position):
        self.__mouse_start_position = position

    def get_participant_id(self):
        return self.config[ConfigKeys.PARTICIPANT_ID.value]

    def get_background_color(self):
        return self.config[ConfigKeys.COLOR_BACKGROUND.value]

    def get_circle_color(self):
        return self.config[ConfigKeys.COLOR_CIRCLES.value]

    def get_target_color(self):
        return self.config[ConfigKeys.COLOR_TARGET.value]

    def get_target_position(self):
        return self.__target_positions[self.__target_position_index]

    def get_circle_size(self):
        return self.__condition[ConfigKeys.CIRCLE_SIZE.value]

    def get_circle_count(self):
        return self.__condition[ConfigKeys.CIRCLE_COUNT.value]

    def get_distraction(self):
        return self.__condition[ConfigKeys.DISTRACTION.value]

    def get_pointer(self):
        return self.config[ConfigKeys.POINTER_TYPE.value]

    def select_next_target(self):
        self.__target_position_index += 1

        if not (self.__target_position_index < len(self.__target_positions)):
            self.__target_position_index = 0
            random.shuffle(self.__target_positions)

            conditions = self.config[ConfigKeys.CONDITIONS.value]
            index = conditions.index(self.__condition) + 1

            if not (index < len(conditions)):
                return False

            self.__condition = conditions[index]

        return True

    def handle_false_clicked(self, mouse_position):
        self.__write_to_stdout_in_csv_format(self.__create_row_data(mouse_position))

    def handle_circle_clicked(self, mouse_position, is_target):
        if is_target:
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
