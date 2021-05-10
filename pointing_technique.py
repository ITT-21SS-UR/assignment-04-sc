"""
TODO description of pointing technique
Upon initialization the pointer gets the available circles.
Filter is called when the mouse is moved.
"""

import time
import math
from evdev import UInput, ecodes as e
from PyQt5 import QtCore

class PointingTechnique:

    capabilities = {
        e.EV_REL : (e.REL_X, e.REL_Y), 
        e.EV_KEY : (e.BTN_LEFT, e.BTN_RIGHT)
    }

    def __get_distance_to_target(self, pos):
        return math.dist([pos.x(), pos.y()], [self.__target_pos.x(), self.__target_pos.y()])

    def __is_in_target(self, x, y):
        pos = QtCore.QPoint(int(x), int(y))
        return self.__get_distance_to_target(pos) <= (self.__target.width() / 2)

    def __is_inside_window(self, x, y):
        parent = self.__target.parent()
        return parent.rect().contains(int(x), int(y))

    def __move_to_target(self, pos):
        if (self.__is_in_target(pos.x(), pos.y())):
            return

        self.__active = True

        dist_x = self.__target_pos.x() - pos.x()
        dist_y = self.__target_pos.y() - pos.y()

        ratio = abs(dist_y / dist_x) if dist_x != 0 else 1

        dir_x = 1 if dist_x >= 0 else -1
        dir_y = 1 if dist_y >= 0 else -1

        delta_x = dir_x * self.__speed if dist_x != 0 else 0
        delta_y = dir_y * self.__speed * ratio

        if delta_y < 1:
            delta_y = 1 / delta_y
            delta_x /= delta_y

        x = pos.x()
        y = pos.y()

        rel_x = math.floor(delta_x + 0.5)
        rel_y = math.floor(delta_y + 0.5)
        
        while (not self.__is_in_target(x, y) and self.__is_inside_window(x, y)):
            x += delta_x
            y += delta_y

            self.__device.write(e.EV_REL, e.REL_X, rel_x)
            self.__device.write(e.EV_REL, e.REL_Y, rel_y)
            self.__device.syn()

            time.sleep(0.01)
        
        self.__active = False

    def __init__(self, target):
        self.__active = False
        self.__device = UInput(self.capabilities)
        self.__target = target
        self.__target_pos = self.__target.geometry().center()
        self.__speed = 2

    def __del__(self):
        self.__device.close()

    def filter(self, current_position):
        if self.__active:
            return

        if self.__get_distance_to_target(current_position) < (self.__target.width() * 2):
            self.__move_to_target(current_position)
        
        # TODO get nearest circle
        # highlight the nearest circle
