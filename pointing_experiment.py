import sys
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtCore import pyqtSignal
from math import dist


class CircleWidget(QtWidgets.QWidget):

    clicked = pyqtSignal()

    def __init__(self, parent = None):
        super(CircleWidget, self).__init__(parent)
        
        self.setAttribute(QtCore.Qt.WA_StaticContents)
        
        self.radius = 0
        self.color = QtGui.QColor("Black")
        self.setMinimumSize(50, 50)
        self.setDiameter(50)

    def setColor(self, color):
        self.color = color
        self.update()

    def setDiameter(self, diameter):
        self.radius = int(diameter / 2)
        self.setFixedSize(diameter, diameter)

    def paintEvent(self, event):
        painter = QtGui.QPainter()
        painter.begin(self)

        painter.setPen(QtGui.QColor("Black"))
        painter.setBrush(self.color)

        rect = event.rect()
        painter.drawEllipse(rect.x(), rect.y(), rect.width() - 1, rect.height() - 1)

        painter.end()

    def mousePressEvent(self, event):
        if dist([self.radius, self.radius], [event.x(), event.y()]) <= self.radius:
            self.clicked.emit()


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setGeometry(550, 200, 800, 600)
        self.setWindowTitle('FittsLawTest')
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setMouseTracking(True)

        self.circles = []
        self.circles.append(CircleWidget(self))

        self.__setup_ui()

    def __setup_ui(self):
        self.setAutoFillBackground(True)
        palette = QtGui.QGuiApplication.palette()
        palette.setColor(QtGui.QPalette.Window, QtGui.QColor("Orange"))
        self.setPalette(palette)

        self.text = "Please click on the target"
        circle = self.circles[0]
        circle.setDiameter(100)
        circle.setColor(QtGui.QColor("Red"))
        circle.move(100, 100)
        circle.clicked.connect(lambda: print("clicked"))

    def mouseMoveEvent(self, event):
        #print(str(event.pos()))
        pass

if __name__ == '__main__':
    # Create the Qt Application
    app = QtWidgets.QApplication(sys.argv)

    # circle = CircleWidget()
    # circle.clicked.connect(lambda: print("circle clicked"))
    # circle.setDiameter(500)
    # circle.show()

    trial = MainWindow()
    trial.show()
    # trial = CircleWidget(50, 50, 100, QtGui.QColor(10, 10, 10))
  
    # Run the main Qt loop
    sys.exit(app.exec_())
