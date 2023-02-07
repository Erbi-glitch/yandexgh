import sys
import os
import sys

import requests
from PyQt5 import QtCore, QtWidgets
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
import math
from frontend import Ui_MainWindow
from random import randint
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
SCREEN_SIZE = [700, 600]
class MyWidget(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.getImage()
        self.initUI()

    def getImage(self):
        type_map = {
            '0': 'l=map',  # обычная
            '1': 'l=map,trf,skl',  # с пробками
            '2': 'l=sat',  # спутник
            '3': 'l=sat,skl',  # гибрид
            '4': 'l=sat,trf,skl'  # гибридная карта с отображением пробок
        }
        location = f'москва'
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
        map_request = f"http://static-maps.yandex.ru/1.x/?ll={coordinate}&spn=0.01,0.01&{type_map['4']}"
        response = requests.get(map_request)

        if not response:
            print("Ошибка выполнения запроса:")
            print(map_request)
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)

        # Запишем полученное изображение в файл.
        self.map_file = "map.png"
        with open(self.map_file, "wb") as file:
            file.write(response.content)

    def initUI(self):
        self.setGeometry(100, 100, *SCREEN_SIZE)
        self.setWindowTitle('Отображение карты')

        ## Изображение
        self.pixmap = QPixmap(self.map_file)
        self.image = QLabel(self)
        self.image.move(250, 80)
        self.image.resize(400, 400)
        self.image.setPixmap(self.pixmap)

    def closeEvent(self, event):
        """При закрытии формы подчищаем за собой"""
        os.remove(self.map_file)


if __name__ == '__main__':
    ap = QApplication(sys.argv)
    scr1 = MyWidget()
    scr1.show()
    sys.exit(ap.exec())
