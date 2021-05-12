#!/usr/bin/python3

import random
import sys
from math import dist

from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtCore import pyqtSignal

from config_parsing import ConfigParsing
from pointing_experiment_model import PointingExperimentModel
from pointing_technique import PointingTechnique

"""
Program has to be executed with sudo else the novel pointer will not work.
We did not use QtGui.QCursor.setPos() because it caused a lot of problems so that we couldn't conduct the study anymore.
E. g. the cursor jumped up and down, the movement is not accurate, does weird things and movement is not possible at all
even when we switched off the mouse cursor integration.
So we decided to place a blue circle in the left corner of the window so that a user has approximately the same
starting position.
Also we didn't test it on Debian but on our main OS (Manjaro) because when we switched off the mouse cursor integration
the Debian VM did not work properly anymore even if no code is executed.

The features of the program were discussed together and everyone got their own tasks.
The authors of the python and sub files are written at the beginning of the python file.
When a main author is mentioned it means that the other person added code for their corresponding tasks/class.
"""


# Main author: Sarah
# Reviewer: Claudia
class CircleWidget(QtWidgets.QWidget):
    clicked = pyqtSignal([QtCore.QPoint])

    def __init__(self, parent=None):
        super(CircleWidget, self).__init__(parent)

        self.setAttribute(QtCore.Qt.WA_StaticContents)
        self.setMouseTracking(True)

        self.__radius = 0
        self.__is_target = False
        self.__target_color = QtGui.QColor("Red")
        self.__color = QtGui.QColor("Black")

        self.setMinimumSize(50, 50)
        self.set_diameter(50)

    def set_color(self, color):
        if self.__color == color:
            return

        self.__color = color
        self.update()

    def set_target_color(self, target_color):
        if self.__target_color == target_color:
            return

        self.__target_color = target_color
        self.update()

    def set_diameter(self, diameter):
        self.__radius = int(diameter / 2)
        self.setFixedSize(diameter, diameter)

    def set_target(self, is_target):
        self.__is_target = is_target
        self.update()

    def is_target(self):
        return self.__is_target

    def paintEvent(self, event):
        painter = QtGui.QPainter()
        painter.begin(self)

        if self.__is_target:
            painter.setPen(self.__target_color)
            painter.setBrush(self.__target_color)
        else:
            painter.setPen(self.__color)
            painter.setBrush(self.__color)

        rect = event.rect()
        painter.drawEllipse(rect.x(), rect.y(), rect.width() - 1, rect.height() - 1)

        painter.end()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton \
                and dist([self.__radius, self.__radius], [event.x(), event.y()]) <= self.__radius:
            self.clicked.emit(event.globalPos())


class MainWindow(QtWidgets.QWidget):
    mouse_target_color = "Blue"

    @staticmethod
    def get_random_pos(max_x, max_y):
        return random.randint(0, max_x), random.randint(0, max_y)

    def __init__(self, config):
        super(MainWindow, self).__init__()

        self.setFixedSize(800, 600)
        self.move(QtWidgets.qApp.desktop().availableGeometry(self).center() - self.rect().center())

        self.setWindowTitle("Fitts Law Test")
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setMouseTracking(True)

        self.__circles = []
        self.__model = PointingExperimentModel(config)
        self.__pointing_technique = None

        self.__color_timer = QtCore.QTimer(self)
        self.__color_timer.setInterval(100)
        self.__color_timer.timeout.connect(self.__on_timeout)
        self.__enable_background_flicker = False

        self.__setup_ui()

    def __setup_ui(self):
        self.setAutoFillBackground(True)
        palette = QtGui.QGuiApplication.palette()
        background_color = QtGui.QColor(self.__model.get_background_color())
        palette.setColor(QtGui.QPalette.Window, background_color)
        self.setPalette(palette)

        mouse_target = CircleWidget(self)
        mouse_target.set_diameter(50)
        mouse_target.set_color(QtGui.QColor(self.mouse_target_color))
        mouse_target.clicked.connect(self.__setup_circles)
        mouse_target.move(0, self.height() - 50)
        self.__mouse_target = mouse_target

        self.__show_intro()

    def __show_intro(self):
        target_color = self.__model.get_target_color().lower()
        mouse_target_color = self.mouse_target_color.lower()
        QtWidgets.QMessageBox.information(self, self.windowTitle(),
                                          "Click on the {0} circle to start and\nthen try to hit the {1} circle".format(
                                              mouse_target_color, target_color))
        self.__clear_screen()

    def __on_timeout(self):
        for circle in self.__circles:
            circle_color = QtGui.QColor(self.__model.get_circle_color())
            circle.set_color(circle_color)

        background_color = QtGui.QColor(self.__model.get_background_color())
        random.choice(self.__circles).set_color(background_color)
        random.choice(self.__circles).set_color(QtGui.QColor("Yellow"))

        if self.__enable_background_flicker:
            palette = self.palette()

            if palette.color(QtGui.QPalette.Window) == background_color:
                palette.setColor(QtGui.QPalette.Window, QtGui.QColor("Yellow"))
            else:
                palette.setColor(QtGui.QPalette.Window, background_color)

            self.setPalette(palette)

    def __circle_clicked(self, position):
        self.__model.handle_circle_clicked(position, self.sender().is_target())

        if self.sender().is_target():
            self.__clear_screen()

    def __clear_screen(self):
        if self.__circles:
            self.__color_timer.stop()

            for circle in self.__circles:
                circle.setParent(None)
                circle.deleteLater()

            self.__circles.clear()
            if not self.__model.select_next_target():
                QtWidgets.QMessageBox.information(self, self.windowTitle(), "Experiment finished!")
                QtWidgets.qApp.quit()
                return

        if self.__enable_background_flicker:
            palette = self.palette()
            palette.setColor(QtGui.QPalette.Window, QtGui.QColor(self.__model.get_background_color()))
            self.setPalette(palette)

        self.__pointing_technique = None
        self.__mouse_target.show()
        self.update()

    def __setup_circles(self):
        self.__model.set_mouse_start_position(self.mapFromGlobal(QtGui.QCursor.pos()))
        self.__mouse_target.hide()
        self.__create_circles(self.__model.get_circle_count(), self.__model.get_circle_size())

        circle_color = QtGui.QColor(self.__model.get_circle_color())
        target_color = QtGui.QColor(self.__model.get_target_color())

        for circle in self.__circles:
            circle.set_color(circle_color)
            circle.set_target_color(target_color)
            circle.show()

        self.update()
        self.__setup_distraction()
        self.__model.start_timer()

    def __setup_distraction(self):
        distraction = self.__model.get_distraction()
        if distraction == "none":
            return

        if distraction == "background_flicker":
            self.__enable_background_flicker = True
            self.__color_timer.setInterval(100)
        elif distraction == "circle_flicker":
            self.__enable_background_flicker = False
            self.__color_timer.setInterval(50)

        self.__color_timer.start()

    def __create_target(self, diameter):
        target = CircleWidget(self)
        target.set_diameter(diameter)
        target.set_target(True)
        target_pos = self.__model.get_target_position()
        target.move(target_pos[0], target_pos[1])
        target.clicked.connect(self.__circle_clicked)
        self.__circles.append(target)

        return target

    def __create_circles(self, count, diameter):
        max_x = self.width() - diameter
        max_y = self.height() - diameter

        target = self.__create_target(diameter)
        self.__pointing_technique = PointingTechnique(target, self.__model.get_threshold(), self.__model.get_density())

        for i in range(0, count - 1):
            (x, y) = self.get_random_pos(max_x, max_y)

            circle = CircleWidget(self)
            circle.set_diameter(diameter)
            circle.move(x, y)

            while self.__has_collision(circle):
                (x, y) = self.get_random_pos(max_x, max_y)
                circle.move(x, y)

            circle.clicked.connect(self.__circle_clicked)
            self.__circles.append(circle)

    def __has_collision(self, new_circle):
        for circle in self.__circles:
            if new_circle.geometry().intersects(circle.geometry()):
                return True

        return False

    def mouseMoveEvent(self, event):
        if self.__pointing_technique and self.__model.get_pointer() == "novel":
            self.__pointing_technique.filter(event.pos())

    def mousePressEvent(self, event):
        # is only called when background is clicked
        if event.button() == QtCore.Qt.LeftButton:
            self.__model.handle_false_clicked(event.pos())


if __name__ == '__main__':
    test_config = ConfigParsing()

    app = QtWidgets.QApplication(sys.argv)

    trial = MainWindow(test_config.get_config())
    trial.show()

    sys.exit(app.exec_())
