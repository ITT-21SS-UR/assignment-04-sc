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

        self.radius = 0
        self.is_target = False
        self.target_color = QtGui.QColor("Red")
        self.color = QtGui.QColor("Black")
        self.setMinimumSize(50, 50)
        self.set_diameter(50)

    def set_color(self, color):
        if self.color == color:
            return

        self.color = color
        self.update()

    def set_diameter(self, diameter):
        self.radius = int(diameter / 2)
        self.setFixedSize(diameter, diameter)

    def set_target(self, is_target):
        self.is_target = is_target
        self.update()

    def is_target(self):
        return self.is_target

    def paintEvent(self, event):
        painter = QtGui.QPainter()
        painter.begin(self)

        if self.is_target:
            painter.setPen(self.target_color)
            painter.setBrush(self.target_color)
        else:
            painter.setPen(self.color)
            painter.setBrush(self.color)

        rect = event.rect()
        painter.drawEllipse(rect.x(), rect.y(), rect.width() - 1, rect.height() - 1)

        painter.end()

    def mousePressEvent(self, event):
        if dist([self.radius, self.radius], [event.x(), event.y()]) <= self.radius:
            self.clicked.emit(event.globalPos())


class MainWindow(QtWidgets.QWidget):
    @staticmethod
    def get_random_pos(max_x, max_y):
        return (random.randint(0, max_x), random.randint(0, max_y))

    def __init__(self, config):
        super(MainWindow, self).__init__()

        self.width = 800
        self.height = 600
        self.setGeometry(550, 200, 800, 600)
        self.setWindowTitle("FittsLawTest")
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setMouseTracking(True)
        self.color_timer = QtCore.QTimer(self)

        self.circles = []

        self.__setup_ui()
        self.color_timer.setInterval(100)
        self.color_timer.timeout.connect(self.__on_timeout)
        self.color_timer.start()

        self.model = PointingExperimentModel(config)

    def __setup_ui(self):
        self.setAutoFillBackground(True)
        palette = QtGui.QGuiApplication.palette()
        palette.setColor(QtGui.QPalette.Window, QtGui.QColor("Orange"))
        self.setPalette(palette)

        self.text = "Please click on the target"
        self.create_circles(20, 100)
        random.choice(self.circles).set_target(True)

    def __on_timeout(self):
        for circle in self.circles:
            circle.set_color(QtGui.QColor("Black"))

        random.choice(self.circles).set_color(QtGui.QColor("Orange"))
        random.choice(self.circles).set_color(QtGui.QColor("Yellow"))

        # palette = self.palette()

        # if palette.color(QtGui.QPalette.Window) == QtGui.QColor("Orange"):
        #     palette.setColor(QtGui.QPalette.Window, QtGui.QColor("Yellow"))
        # else:
        #     palette.setColor(QtGui.QPalette.Window, QtGui.QColor("Orange"))

        # self.setPalette(palette)


    def __circle_clicked(self, position):
        if self.sender().is_target:
            print("ooops I did it again")

        self.model.handle_circle_clicked(position)

    def create_circles(self, count, diameter):
        max_x = self.width - diameter
        max_y = self.height - diameter

        for i in range(0, count):
            (x, y) = self.get_random_pos(max_x, max_y)

            circle = CircleWidget(self)
            circle.set_diameter(diameter)
            circle.move(x, y)

            while self.has_collision(circle, self.circles):
                (x, y) = self.get_random_pos(max_x, max_y)
                circle.move(x, y)

            circle.clicked.connect(self.__circle_clicked)
            self.circles.append(circle)

    def has_collision(self, current_item, items):
        for circle in items:
            if current_item.geometry().intersects(circle.geometry()):
                return True

        return False

    def mouseMoveEvent(self, event):
        # TODO(claudi) start timer
        pass

    def mousePressEvent(self, event):
        # is only activated when no circle is clicked
        if event.button() == QtCore.Qt.LeftButton:
            self.model.handle_false_clicked(event.pos())


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
    # TODO check if file contains correct and all relevant data?
    test_config = read_test_config()

    # Create the Qt Application
    app = QtWidgets.QApplication(sys.argv)

    trial = MainWindow(test_config)
    trial.show()
 
    # Run the main Qt loop
    sys.exit(app.exec_())
