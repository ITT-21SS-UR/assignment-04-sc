import math
import time

from PyQt5 import QtWidgets
from evdev import UInput, ecodes as e

"""
Our pointing technique supports users by moving the cursor to the target when it is near the target.
We use linear interpolation to move the mouse to the target.

Upon initialization the pointer gets the target, threshold (%) and density as parameters.
UInput is used to move the mouse because setting the cursor position caused a lot of problems.

Filter is called when the mouse is moved and the novel pointer is activated.
The filter method gets the current position of the mouse and moves the pointer to the target
when the distance to the target falls under the threshold.

When the pointer is in the center? of the target the cursor stops its movement.
When the user clicks the target the device closes so that the cursor is not moved anymore.
"""


# Author: Sarah
# Reviewer: Claudia
class PointingTechnique:
    capabilities = {
        e.EV_REL: (e.REL_X, e.REL_Y),
        e.EV_KEY: (e.BTN_LEFT, e.BTN_RIGHT)
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

        n = self.__density  # The smaller n is the "faster" the mouse becomes
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

    def __init__(self, target, threshold, density):
        self.__moving = False
        self.__device = UInput(self.capabilities)
        self.__target = target
        self.__target_pos = self.__target.geometry().center()
        self.__current_pos = None

        self.__threshold = threshold
        self.__density = density

    def __del__(self):
        self.__device.close()

    def filter(self, current_pos):
        self.__current_pos = current_pos

        threshold = int(self.__target.parent().width() * self.__threshold)
        if self.__get_distance_to_target(current_pos) < threshold:
            self.__move_to_target()
