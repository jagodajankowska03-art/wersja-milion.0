import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QLabel, QLineEdit, QMessageBox
)
from PyQt5.QtGui import QPainter, QPen, QPixmap
from PyQt5.QtCore import Qt
import math
# -------------------------
# 1. Klasy danych
# -------------------------
class Point:
    def __init__(self, name, lon, lat, priority=0):
        self.name = name
        self.lon = lon
        self.lat = lat
        self.priority = priority
    def __repr__(self):
        return f"{self.name} ({self.lon}, {self.lat})"
class Route:
    def __init__(self):
        self.points = []
    def add_point(self, point):
        self.points.append(point)
    def remove_point(self, point):
        self.points.remove(point)
    def calculate_distance(self):
        dist = 0
        for i in range(len(self.points)-1):
            dx = self.points[i+1].lon - self.points[i].lon
            dy = self.points[i+1].lat - self.points[i].lat
            dist += math.sqrt(dx**2 + dy**2)
        return dist
    def optimize_route(self):
        if not self.points:
            return
        sorted_points = sorted(self.points, key=lambda p: -p.priority)
        optimized = [sorted_points[0]]
        remaining = sorted_points[1:]
        while remaining:
            last = optimized[-1]
            next_point = min(remaining, key=lambda p: (p.lon - last.lon)**2 + (p.lat - last.lat)**2)
            optimized.append(next_point)
            remaining.remove(next_point)
        self.points = optimized
# -------------------------
# 2. Canvas z mapą
# -------------------------
class MapCanvas(QWidget):
    def __init__(self, route):
        super().__init__()
        self.route = route
        self.map_image = QPixmap("mazowieckie_map.png")  # tło mapy offline
        self.setMinimumSize(self.map_image.width(), self.map_image.height())
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.map_image)
        pen = QPen(Qt.red, 4)
        painter.setPen(pen)
        # Rysowanie punktów
        for p in self.route.points:
            x, y = self.geo_to_canvas(p.lon, p.lat)
            painter.drawEllipse(x-4, y-4, 8, 8)
            painter.drawText(x+5, y-5, p.name)
        # Rysowanie linii tras
        for i in range(len(self.route.points)-1):
            x1, y1 = self.geo_to_canvas(self.route.points[i].lon, self.route.points[i].lat)
            x2, y2 = self.geo_to_canvas(self.route.points[i+1].lon, self.route.points[i+1].lat)
            painter.drawLine(x1, y1, x2, y2)
    def geo_to_canvas(self, lon, lat):
        # Granice Mazowsza dla mapy w px
        minx, miny, maxx, maxy = 20.5, 51.0, 22.0, 53.0
        width, height = self.map_image.width(), self.map_image.height()
        x = int((lon - minx) / (maxx - minx) * width)
        y = int((maxy - lat) / (maxy - miny) * height)
        return x, y
# -------------------------
# 3. GUI główne
# -------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Optymalizacja Tras – Mazowsze")
        self.route = Route()
        self.initUI()
    def initUI(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout()
        central.setLayout(layout)
        # Lewa kolumna
        left = QVBoxLayout()
        self.point_list = QListWidget()
        self.name_input = QLineEdit()
        self.lon_input = QLineEdit()
        self.lat_input = QLineEdit()
        add_btn = QPushButton("Dodaj punkt")
        add_btn.clicked.connect(self.add_point)
        optimize_btn = QPushButton("Optymalizuj trasę")
        optimize_btn.clicked.connect(self.optimize_route)
        left.addWidget(QLabel("Nazwa punktu:"))
        left.addWidget(self.name_input)
        left.addWidget(QLabel("Długość geograficzna (lon):"))
        left.addWidget(self.lon_input)
        left.addWidget(QLabel("Szerokość geograficzna (lat):"))
        left.addWidget(self.lat_input)
        left.addWidget(add_btn)
        left.addWidget(optimize_btn)
        left.addWidget(self.point_list)
        # Prawa kolumna – mapa
        self.map_canvas = MapCanvas(self.route)
        layout.addLayout(left)
        layout.addWidget(self.map_canvas)
    def add_point(self):
        try:
            name = self.name_input.text()
            lon = float(self.lon_input.text())
            lat = float(self.lat_input.text())
            point = Point(name, lon, lat)
            self.route.add_point(point)
            self.point_list.addItem(str(point))
            self.map_canvas.update()
        except ValueError:
            QMessageBox.warning(self, "Błąd", "Lon i Lat muszą być liczbami")
    def optimize_route(self):
        self.route.optimize_route()
        self.point_list.clear()
        for p in self.route.points:
            self.point_list.addItem(str(p))
        self.map_canvas.update()
# -------------------------
# 4. Uruchomienie aplikacji
# -------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())












Jot something down









