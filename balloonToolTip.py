from aqt import QLabel, QPoint, QToolTip, QVBoxLayout,QCheckBox
from aqt import QPainter, QPainterPath, QPen, QColor
from aqt import Qt, QRectF,QWidget

class BalloonToolTip(QWidget):
    def __init__(self, text, parent:QCheckBox=None):
        super().__init__(parent)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.label = QLabel(text)
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

        parent.enterEvent = self.showBalloonToolTip
        parent.leaveEvent = self.hideBalloonToolTip

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect().adjusted(0, 0, -10, -10)), 10, 10)
        path.moveTo(self.rect().right() - 20, self.rect().bottom() - 10)
        path.lineTo(self.rect().right() - 10, self.rect().bottom())
        path.lineTo(self.rect().right() - 10, self.rect().bottom() - 10)
        painter.fillPath(path, self.palette().window())
        pen = QPen(QColor(0, 0, 0), 1)
        painter.setPen(pen)
        painter.drawPath(path)

    def showBalloonToolTip(self, event):
        self.move(self.parent().mapToGlobal(QPoint(0, self.parent().height())))
        self.show()

    def hideBalloonToolTip(self, event):
        self.hide()
