import sys
import os
import sys
from PyQt5 import Qt
import requests
from PyQt5 import QtCore, QtWidgets
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
import math
from frontend import Ui_MainWindow
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QLabel

SCREEN_SIZE = [700, 600]


class MyWidget(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # TEST
        self.pushButton.clicked.connect(self.on_load)
        self.nam = Qt.QNetworkAccessManager()
        self.nam.finished.connect(self.finish_request)

    def getImage(self):

        type_map = {
            '0': 'l=map',  # обычная
            '1': 'l=map,trf,skl',  # с пробками
            '2': 'l=sat',  # спутник
            '3': 'l=sat,skl',  # гибрид
            '4': 'l=sat,trf,skl'  # гибридная карта с отображением пробок
        }
        location = f'улица Космонавтов город Москва'
        georesponse = requests.get(
            f"http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode={location}&format=json")
        json_response = georesponse.json()

        # Получаем первый топоним из ответа геокодера.
        # Согласно описанию ответа, он находится по следующему пути:
        toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        # Название:
        toponym_address = toponym["metaDataProperty"]["GeocoderMetaData"]["text"]
        # Координаты:
        toponym_coodrinates = toponym["Point"]["pos"]
        coordinate = list(toponym_coodrinates.split())
        coordinate = ','.join(coordinate)
        print(coordinate)
        print(type_map[self.map_type()])
        self.map_request = f"http://static-maps.yandex.ru/1.x/?ll={coordinate}&spn=0.001,0.001&{type_map[self.map_type()]}&pt={coordinate},comma"

    def map_type(self):
        if self.map_sputnik.isChecked():
            return '2'
        elif self.map_hybrid.isChecked():
            return '3'
        else:
            return '0'

    def on_load(self):
        print("Load image")
        self.getImage()
        url = self.map_request
        print(url)
        self.nam.get(Qt.QNetworkRequest(Qt.QUrl(url)))

    def finish_request(self, reply):
        img = Qt.QPixmap()
        img.loadFromData(reply.readAll())
        self.label_2.setPixmap(img)


if __name__ == '__main__':
    ap = QApplication(sys.argv)
    scr1 = MyWidget()
    scr1.show()
    sys.exit(ap.exec())
