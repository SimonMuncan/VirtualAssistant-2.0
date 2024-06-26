
import random
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QFont,  QPainter, QColor, QPolygonF, QBrush
from PyQt6.QtCore import Qt, QPointF
from wheather import Weather

class RainbowBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.value = 0

    def setValue(self, value):
        self.value = value
        self.update()

    def setRandomValue(self):
        random_value = Weather.airQuality()
        #random_value = random.randint(0, 300)
        self.setValue(random_value)

    def paintEvent(self, event):
        painter = QPainter(self)
        self.drawRainbowBar(painter)
        self.drawArrow(painter)
        
    def drawRainbowBar(self, painter):
        gradient_colors = [
            Qt.GlobalColor.green, Qt.GlobalColor.yellow ,QColor(255, 165, 0) ,
            Qt.GlobalColor.red, Qt.GlobalColor.magenta, Qt.GlobalColor.darkRed 
        ]
        
        bar_height = self.height()
        segment_height = int(bar_height / len(gradient_colors))
        
        for i, color in enumerate(gradient_colors):
            painter.setBrush(QBrush(color))
            painter.drawRect(0, int(i * segment_height), self.width(), int(segment_height))


    def drawArrow(self, painter):
        arrow_pos = int(self.height() * self.value / 300)
        arrow_width = int(self.width() * 0.4)
        arrow_height = int(self.width() * 0.2)

        arrow = QPolygonF()
        arrow.append(QPointF(self.width(), arrow_pos))
        arrow.append(QPointF(self.width() - arrow_width, arrow_pos - arrow_height))
        arrow.append(QPointF(self.width() - arrow_width, arrow_pos + arrow_height))
        
        painter.setBrush(QBrush(Qt.GlobalColor.black))
        painter.drawPolygon(arrow)

        painter.setFont(QFont("Arial", 11))
        text = f"{self.value}"
        text_width = painter.fontMetrics().horizontalAdvance(text)
        painter.drawText(int(self.width() - arrow_width - text_width - 5), int(arrow_pos + 5), text)
