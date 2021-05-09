#!/usr/bin/python3

import configparser
import json
import os
import random
import sys
from math import dist

from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtCore import pyqtSignal

from pointing_experiment_model import PointingExperimentModel


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
    @staticmethod
    def get_random_pos(max_x, max_y):
        return random.randint(0, max_x), random.randint(0, max_y)

    def __init__(self, config):
        super(MainWindow, self).__init__()

        self.setFixedSize(800, 600)
        self.move(QtWidgets.qApp.desktop().availableGeometry(self).center() - self.rect().center())

        self.setWindowTitle("FittsLawTest")
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setMouseTracking(True)

        self.__circles = []
        self.__model = PointingExperimentModel(config)

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

        self.__show_intro()

    def __show_intro(self):
        target_color = self.__model.get_target_color().lower()
        QtWidgets.QMessageBox.information(self, self.windowTitle(), "Click on the {0} circle".format(target_color))
        self.__setup_circles()

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
            self.__setup_circles()

    def __setup_circles(self):
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

        self.__create_circles(self.__model.get_circle_count(), self.__model.get_circle_size())

        circle_color = QtGui.QColor(self.__model.get_circle_color())
        target_color = QtGui.QColor(self.__model.get_target_color())

        for circle in self.__circles:
            circle.set_color(circle_color)
            circle.set_target_color(target_color)
            circle.show()

        self.update()
        self.__setup_distraction()
        # QtGui.QCursor.setPos(self.mapToGlobal(self.rect().bottomLeft()))

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

    def __create_circles(self, count, diameter):
        max_x = self.width() - diameter
        max_y = self.height() - diameter

        # for i in range(0, 5):
        #     print(str(self.get_random_pos(max_x, max_y)))

        target = CircleWidget(self)
        target.set_diameter(diameter)
        target.set_target(True)
        target_pos = self.__model.get_target_position()
        target.move(target_pos[0], target_pos[1])
        target.clicked.connect(self.__circle_clicked)
        self.__circles.append(target)

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
        self.__model.start_timer()

    def mousePressEvent(self, event):
        # is only called when background is clicked
        if event.button() == QtCore.Qt.LeftButton:
            self.__model.handle_false_clicked(event.pos())


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
    # TODO check if file contains correct and all relevant data; at the end check if a key is missing?
    test_config = read_test_config()

    app = QtWidgets.QApplication(sys.argv)

    trial = MainWindow(test_config)
    trial.show()

    sys.exit(app.exec_())
