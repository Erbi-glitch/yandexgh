import sys
from PyQt5 import Qt, QtCore
import requests
from PyQt5.QtWidgets import QMainWindow
from frontend import Ui_MainWindow
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt as Qt_mouse
import math

SCREEN_SIZE = [700, 700]


def lonlat_distance(a, b):
    degree_to_meters_factor = 111 * 1000
    a_lon, a_lat = a
    b_lon, b_lat = b
    radians_lattitude = math.radians((a_lat + b_lat) / 2.)
    lat_lon_factor = math.cos(radians_lattitude)
    dx = abs(a_lon - b_lon) * degree_to_meters_factor * lat_lon_factor
    dy = abs(a_lat - b_lat) * degree_to_meters_factor
    distance = math.sqrt(dx * dx + dy * dy)
    return distance


api_key = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"
search_api_server = "https://search-maps.yandex.ru/v1/"

map_api_server = "http://static-maps.yandex.ru/1.x/"
geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"


class MyWidget(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.map_scale = 0.001
        self.map_x = 0
        self.map_y = 0
        self.point_position_x = None
        self.point_position_y = None
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
        self.point_position_global = None

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
        self.point_position_global = toponym['boundedBy']['Envelope']
        # Название:
        toponym_address = toponym["metaDataProperty"]["GeocoderMetaData"]["text"]
        # Координаты:
        toponym_coordinates = toponym["Point"]["pos"].split()
        print(toponym_address)
        print(toponym_coordinates)

        y = str(float(toponym_coordinates[0]) + self.map_y)
        x = str(float(toponym_coordinates[1]) + self.map_x)
        self.point_position_y = float(y)
        self.point_position_x = float(x)
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
        # print(coordinate)
        # print(toponym['boundedBy']['Envelope'])
        # print(type_map[self.map_change_type()])
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
        self.map_scale = round(self.map_scale, 8)
        print(self.map_scale)
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

    def mousePressEvent(self, event):
        if event.button() == Qt_mouse.LeftButton:

            if self.point_position_global and 273 < event.x() < 749 and 102 < event.y() < 487:
                try:

                    qx = round(self.point_position_x + self.map_scale - (event.x() / 749) * self.map_scale, 7)
                    qy = round(self.point_position_y + self.map_scale - (490 / event.y()) * self.map_scale + 0.0004, 7)
                    # print(self.point_position_x,self.map_scale,(event.x()/749)*self.map_scale*2)
                    print(qx, qy)
                    geocoder_request = f"http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode={str(qy)},{str(qx)}&format=json"
                    response = requests.get(geocoder_request)
                    json_response = response.json()
                    toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
                    toponym_address = toponym["metaDataProperty"]["GeocoderMetaData"]["text"]
                    print(toponym_address)
                    self.textBrowser.append(f'\n Вы выбрали {toponym_address}')

                except Exception as e:
                    print(e)

        elif event.button() == Qt_mouse.RightButton:
            if self.point_position_global and 273 < event.x() < 749 and 102 < event.y() < 487:
                try:

                    qx = round(self.point_position_x + self.map_scale - (event.x() / 749) * self.map_scale, 7)
                    qy = round(self.point_position_y + self.map_scale - (490 / event.y()) * self.map_scale + 0.0007, 7)
                    # print(self.point_position_x,self.map_scale,(event.x()/749)*self.map_scale*2)
                    print(qx, qy)
                    geocoder_request = f"http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode={str(qy)},{str(qx)}&format=json"
                    response = requests.get(geocoder_request)
                    json_response = response.json()
                    toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
                    toponym_address = toponym["metaDataProperty"]["GeocoderMetaData"]["text"]

                    search_params = {
                        "apikey": api_key,
                        "text": toponym_address,
                        "lang": "ru_RU",
                        "ll": f'{str(qy)},{str(qx)}',
                        "spn": f'{self.map_scale},{self.map_scale}',
                        "type": "biz"
                    }
                    response = requests.get(search_api_server, params=search_params)

                    json_response = response.json()

                    organization = json_response["features"][0]
                    org_name = organization["properties"]["CompanyMetaData"]["name"]
                    org_address = organization["properties"]["CompanyMetaData"]["address"]
                    point = organization["geometry"]["coordinates"]
                    org_point = f"{point[0]},{point[1]}"

                    qqqqq = round(lonlat_distance([qy, qx], list(map(float, point))), 3)
                    print(json_response, qqqqq)
                    if qqqqq < 100:
                        self.textBrowser.append(f'\n Вы выбрали \n{org_name}  ')

                    else:
                        self.textBrowser.append(f'Повторите запрос')


                except Exception as e:
                    print(e)


if __name__ == '__main__':
    ap = QApplication(sys.argv)
    scr1 = MyWidget()
    scr1.show()
    sys.exit(ap.exec())
'''
[[54.63874909348456,55.62914664782716],[54.8312557744172,56.288326335327156]]►
[[53.95771679524626,53.32201774157716],[55.497817707334384,58.59545524157716]]
[[54.734365297279616,55.95616157092289],[54.73586925498853,55.96131141223149]]
'''
