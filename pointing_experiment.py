import sys, random
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtCore import pyqtSignal
from math import dist


class CircleWidget(QtWidgets.QWidget):

    clicked = pyqtSignal()

    def __init__(self, parent = None):
        super(CircleWidget, self).__init__(parent)
        
        self.setAttribute(QtCore.Qt.WA_StaticContents)
        self.setMouseTracking(True)
        
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
        self.width = 800
        self.height = 600
        self.setGeometry(550, 200, 800, 600)
        self.setWindowTitle('FittsLawTest')
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setMouseTracking(True)

        self.circles = []
        # self.circles.append(CircleWidget(self))

        self.__setup_ui()

    def __setup_ui(self):
        self.setAutoFillBackground(True)
        palette = QtGui.QGuiApplication.palette()
        palette.setColor(QtGui.QPalette.Window, QtGui.QColor("Orange"))
        self.setPalette(palette)

        self.text = "Please click on the target"
        self.create_circles(30, 50)
        # circle = self.circles[0]
        # circle.setDiameter(100)
        # circle.setColor(QtGui.QColor("Red"))
        # circle.move(100, 100)
        # circle.clicked.connect(lambda: print("clicked"))

    
    def create_circles(self, count, diameter):
        min_x_y = diameter
        max_x = self.width - diameter
        max_y = self.height - diameter
        pos = []

        i = 0
        while i < count:
            x = self.genRandNum(min_x_y, max_x)
            y = self.genRandNum(min_x_y, max_y)
            
            circle = CircleWidget(self)
            circle.setDiameter(diameter)
            circle.move(x, y)

            if self.check_collision(circle, self.circles):
                circle.destroy()
            
            self.circles.append(circle)
            i += 1

    def check_collision(self, current_item, items):
        # QtWidgets.QGraphicsItem.collidesWithItem
        for i in range (0, len(items)):
            if current_item.rect().intersects(items[i].rect()):
                return True
        return False

    def genRandNum(self, min, max):
        return random.randint(min, max)
    
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
