import sys
from mainUI import Ui_optionAtillaWindow
from optionAtilla import Atilla
from PyQt6 import QtCore
from PyQt6.QtWidgets import QApplication, QMainWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = QMainWindow()
    ui = Ui_optionAtillaWindow()
    ui.setupUi(window)
    ui.pushButtonClearSelection.setEnabled(False)
    ui.pushButtonClearTrades.setEnabled(False)
    ui.pushButtonCancelOrders.setEnabled(False)
    ui.pushButtonCompute.setEnabled(False)
    ui.pushButtonDisplay.setEnabled(False)
    ui.pushButtonFetch.setEnabled(False)
    ui.pushButtonLiquidate.setEnabled
    atilla = Atilla(app, "config\\config.ini")
    atilla.setWindow(ui)
    window.show()
    sys.exit(app.exec())