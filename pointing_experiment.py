import sys
from PyQt5 import QtGui, QtWidgets, QtCore


class CircleWidget(QtWidgets.QWidget):

    def __init__(self, x_pos, y_pos, size, color):
        super(CircleWidget, self).__init__()
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.size = size
        self.color = color

    def draw_circle(self, q_painter):
        q_painter.setPen(QtGui.QColor(0, 0, 0))
        q_painter.setBrush(self.color)
        q_painter.drawEllipse(self.x_pos, self.y_pos, self.size, self.size)

class MainWindow(QtWidgets.QTabWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.__setup_ui()

    def __setup_ui(self):
        self.text = "Please click on the target"
        self.setGeometry(550, 200, 800, 600)
        self.setWindowTitle('FittsLawTest')
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        # QtGui.QCursor.setPos(self.mapToGlobal(
            # QtCore.QPoint(self.start_pos[0], self.start_pos[1])))
        self.setMouseTracking(True)
        self.show()

    def draw_background(self, event, qp, color):
        qp.setBrush(color)
        qp.drawRect(event.rect())

    def draw_circles(self, q_painter):
        circle = CircleWidget(50, 50, 50, QtGui.QColor(31, 60, 242))
        circle.draw_circle(q_painter)

        circle2 = CircleWidget(300, 350, 50, QtGui.QColor(242, 31, 31))
        circle2.draw_circle(q_painter)
    
    def paintEvent(self, event):
        q_painter = QtGui.QPainter()
        q_painter.begin(self)

        self.draw_background(event, q_painter, QtGui.QColor(245, 194, 66)) # orange
        self.draw_circles(q_painter)

        q_painter.end()

if __name__ == '__main__':
    # Create the Qt Application
    app = QtWidgets.QApplication(sys.argv)
    trial = MainWindow()
    # trial = CircleWidget(50, 50, 100, QtGui.QColor(10, 10, 10))
  
    # Run the main Qt loop
    sys.exit(app.exec_())
