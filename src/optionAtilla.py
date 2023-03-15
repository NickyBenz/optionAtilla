import configparser
from account_data import AccountData
from account_model import AccountModel
from deribit_ws import Deribit_WS
from PyQt6 import QtCore


class Atilla(QtCore.QObject):
	def __init__(self, parent, config_file):
		super().__init__(parent)
		self.parent = parent
		self.currency = None
		self.account = AccountData()
		self.account_model = AccountModel(parent)
		self.account_model.update(self.account)
		self.cfg = configparser.ConfigParser()
		self.cfg.read(config_file)
		self.client = None
		self.window = None


	def setWindow(self, window):
		self.window = window
		self.window.tableViewAccount.setModel(self.account_model)
		self.window.pushButtonConnect.clicked.connect(self.connect)
		QtCore.QMetaObject.connectSlotsByName(self)
    

	def authenticate(self):
		self.client.authenticate()

	def getAccount(self):
		self.client.account_summary("BTC")

	def connect(self, currency, prod=False):
		if self.client is not None:
			self.client.close()
			self.client = None
			self.account.clear()
		
		self.client = Deribit_WS(self.parent)
		key = "TEST" if not prod else "PROD"
		self.client.connect(self, self.cfg[key]["api_key"], self.cfg[key]['api_secret'], self.cfg[key]['ws_url'])
		QtCore.QTimer.singleShot(3000, self.authenticate)
		QtCore.QTimer.singleShot(6000, self.getAccount)


	def onAccountData(self, dict_obj):
		self.account.update(dict_obj)
		self.window.tableViewAccount.viewport().update()


	def disconnect(self):
		if self.client is not None:
			self.client.close()
			self.client = None
		self.account.clear()

	


		