import sys

from PyQt6 import QtCore, QtWebSockets, QtNetwork
from PyQt6.QtCore import QUrl, QCoreApplication, QTimer
from PyQt6.QtWidgets import QApplication
from deribit_ws import Deribit_WS

def quit_app():
    print("timer timeout - exiting")
    QCoreApplication.quit()

def authenticate():
    client.authenticate()

def subscribe():
    client.account_summary("BTC")

if __name__ == '__main__':
    global client
    app = QApplication(sys.argv)
    QTimer.singleShot(60000, quit_app)
    client = Deribit_WS(app)
    client.connect('1CRbJJGy', 'LumITG74SLMKa5RwP29Np0HTsofGTJ1zWKEYIAaU8z4', 'wss://test.deribit.com/ws/api/v2')
    QTimer.singleShot(2000, authenticate)
    QTimer.singleShot(7000, subscribe)
    app.exec()