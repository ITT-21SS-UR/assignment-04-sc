"""
TODO description of pointing technique
Upon initialization the pointer gets the available circles.
Filter is called when the mouse is moved.
"""

import time
import math
from evdev import UInput, ecodes as e
from PyQt5 import QtWidgets

class PointingTechnique:

    capabilities = {
        e.EV_REL : (e.REL_X, e.REL_Y), 
        e.EV_KEY : (e.BTN_LEFT, e.BTN_RIGHT)
    }

    def __get_distance_to_target(self, pos):
        return math.dist([pos.x(), pos.y()], [self.__target_pos.x(), self.__target_pos.y()])

    def __is_in_target(self, pos):
        return self.__get_distance_to_target(pos) <= (self.__target.width() / 2)

    # https://en.wikipedia.org/wiki/Linear_interpolation
    # https://stackoverflow.com/questions/49173095/how-to-move-an-object-along-a-line-given-two-points#49173439
    def __move_to_target(self):
        if self.__moving or self.__is_in_target(self.__current_pos):
            return

        self.__moving = True

        # TODO move "20" to config
        n = 20
        x0, y0 = self.__current_pos.x(), self.__current_pos.y()
        x1, y1 = self.__target_pos.x(), self.__target_pos.y()
        x_t0, y_t0 = x0, y0

        for i in range(0, n):
            if self.__is_in_target(self.__current_pos):
                return

            t = i / n
            x_t = (1.0 - t) * x0 + t * x1
            y_t = (1.0 - t) * y0 + t * y1

            rel_x = int(x_t - x_t0)
            rel_y = int(y_t - y_t0)

            self.__device.write(e.EV_REL, e.REL_X, rel_x)
            self.__device.write(e.EV_REL, e.REL_Y, rel_y)
            self.__device.syn()

            x_t0, y_t0 = x_t, y_t

            time.sleep(0.01)
            QtWidgets.qApp.processEvents()

        self.__moving = False

    def __init__(self, target):
        self.__moving = False
        self.__device = UInput(self.capabilities)
        self.__target = target
        self.__target_pos = self.__target.geometry().center()
        self.__current_pos = None

    def __del__(self):
        self.__device.close()

    def filter(self, current_pos):
        self.__current_pos = current_pos

        # TODO move "0.33" to config
        threshold = int(self.__target.parent().width() * 0.33)
        if self.__get_distance_to_target(current_pos) < threshold:
            self.__move_to_target()
