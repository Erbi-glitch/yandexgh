import sys
from PyQt5 import Qt, QtCore
import requests
from PyQt5.QtWidgets import QMainWindow
from frontend import Ui_MainWindow
from PyQt5.QtWidgets import QApplication

SCREEN_SIZE = [700, 700]


class MyWidget(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.map_scale = 0.001
        self.map_x = 0
        self.map_y = 0
        self.map_points = []
        self.is_find = False

        self.setupUi(self)
        self.pushButton.clicked.connect(self.find_point)
        self.pushButton_2.clicked.connect(self.clear_points)
        self.map_up.clicked.connect(self.map_change_coordinates)
        self.map_down.clicked.connect(self.map_change_coordinates)
        self.map_left.clicked.connect(self.map_change_coordinates)
        self.map_right.clicked.connect(self.map_change_coordinates)
        self.mail_true.stateChanged.connect(self.mail_update)
        self.horizontalSlider.setRange(1, 7000)
        self.horizontalSlider.setPageStep(1)
        self.horizontalSlider.valueChanged.connect(self.map_change_scale)
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
        location = self.lineEdit.text()
        georesponse = requests.get(
            f"http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode={location}&format=json")
        json_response = georesponse.json()

        # Получаем первый топоним из ответа геокодера.
        # Согласно описанию ответа, он находится по следующему пути:
        toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        # Название:
        toponym_address = toponym["metaDataProperty"]["GeocoderMetaData"]["text"]
        # Координаты:
        toponym_coordinates = toponym["Point"]["pos"].split()
        print(toponym_address)
        print(toponym_coordinates)
        y = str(float(toponym_coordinates[0]) + self.map_y)
        x = str(float(toponym_coordinates[1]) + self.map_x)
        print(toponym_coordinates)
        print(self.mail_true.isChecked())

        if self.mail_true.isChecked():
            mail = toponym['metaDataProperty']['GeocoderMetaData']['Address']
            if 'postal_code' in mail.keys():
                mail = mail['postal_code']
            else:
                mail = 'Нет корректного почтового адреса'

            toponym_address += '\n Почтовый адрес: ' + mail

        self.textBrowser.setText(toponym_address)
        coordinate = [y, x]
        coordinate = ','.join(coordinate)
        if self.is_find:
            self.map_points.append(','.join(toponym_coordinates))
            self.is_find = False
        print(coordinate)
        print(type_map[self.map_change_type()])
        if self.map_points:
            self.map_request = f"http://static-maps.yandex.ru/1.x/?ll={coordinate}&spn={self.map_scale},{self.map_scale}&{type_map[self.map_change_type()]}&pt={'~'.join(self.map_points)},comma"
        else:
            self.map_request = f"http://static-maps.yandex.ru/1.x/?ll={coordinate}&spn={self.map_scale},{self.map_scale}&{type_map[self.map_change_type()]}"
        print(self.map_request)

    def map_change_type(self):
        if self.map_sputnik.isChecked():
            return '2'
        elif self.map_hybrid.isChecked():
            return '3'
        else:
            return '0'

    def map_change_scale(self, value):
        self.map_scale = value / 1000
        self.on_load()

    def map_change_coordinates(self):
        move = self.sender().text()
        if move == 'Вверх':
            self.map_x += 0.0001 * self.map_scale * 1000

        elif move == 'Вниз':
            self.map_x -= 0.0001 * self.map_scale * 1000
        elif move == 'Лево':
            self.map_y -= 0.0001 * self.map_scale * 1000
        elif move == 'Право':
            self.map_y += 0.0001 * self.map_scale * 1000
        self.on_load()

    def find_point(self):
        self.is_find = True
        self.on_load()

    def clear_points(self):
        self.lineEdit.setText('')
        self.map_points = []

    # code

    def on_load(self):
        print("Load image")
        self.getImage()
        url = self.map_request
        self.nam.get(Qt.QNetworkRequest(Qt.QUrl(url)))

    def finish_request(self, reply):
        img = Qt.QPixmap()
        img.loadFromData(reply.readAll())
        self.label_2.setPixmap(img)

    def mail_update(self):
        try:
            self.getImage()
        except:
            self.textBrowser.setText('Вы не ввели адрес')
        print('Update')


if __name__ == '__main__':
    ap = QApplication(sys.argv)
    scr1 = MyWidget()
    scr1.show()
    sys.exit(ap.exec())
