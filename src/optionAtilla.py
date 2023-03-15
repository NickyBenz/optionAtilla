import configparser
import json
from account_data import AccountData
from position_data import PositionData
from account_model import AccountModel
from position_model import PositionModel
from deribit_rest import RestClient
from deribit_ws import Deribit_WS
from PyQt6 import QtCore


class Atilla(QtCore.QObject):
	def __init__(self, parent, config_file):
		super().__init__(parent)
		self.parent = parent
		self.currency = None
		self.account = AccountData()
		self.positions = PositionData()
		self.account_model = AccountModel(parent)
		self.position_model = PositionModel(parent)
		self.account_model.update(self.account)
		self.position_model.update(self.positions)
		self.cfg = configparser.ConfigParser()
		self.cfg.read(config_file)
		self.client_ws = None
		self.client_rest = None
		self.window = None


	def setWindow(self, window):
		self.window = window
		self.window.tableViewAccount.setModel(self.account_model)
		self.window.tableViewPositions.setModel(self.position_model)
		self.window.pushButtonConnect.clicked.connect(self.connect)
		self.window.pushButtonClose.clicked.connect(self.close)
		self.window.pushButtonFetch.clicked.connect(self.fetch)
		QtCore.QMetaObject.connectSlotsByName(self)

	def close(self):
		self.disconnect()
		self.window.centralwidget.close()

	def authenticate(self):
		self.client_ws.authenticate()

	def getChanges(self):
		curr = self.window.comboCurr.currentText()
		self.client_ws.account_summary(curr)
		self.client_ws.change_summary(curr)


	def connect(self):
		if self.client_ws is not None:
			self.client_ws.close()
			self.client_ws = None
			self.account.clear()
		key = self.window.comboEnv.currentText()
		curr = self.window.comboCurr.currentText()

		api_key = self.cfg[key]["api_key"]
		api_secret = self.cfg[key]["api_secret"]
		rest_url = self.cfg[key]["rest_url"]
		ws_url = self.cfg[key]["ws_url"]

		self.client_rest = RestClient(api_key, api_secret, rest_url)
		positions = self.client_rest.getpositions(curr, "option")
		orderres = self.client_rest.getopenorders(curr, "option")
		self.onPositionData(positions)
		self.client_ws = Deribit_WS(self.parent)
		self.client_ws.connect(self, api_key, api_secret, ws_url)
		QtCore.QTimer.singleShot(3000, self.authenticate)
		QtCore.QTimer.singleShot(6000, self.getChanges)
	

	def onAccountData(self, dict_obj):
		self.account.update(dict_obj)
		self.window.tableViewAccount.viewport().update()

	def onPositionData(self, positions):
		self.position_model.beginResetModel()
		self.positions.update(positions)
		self.position_model.endResetModel()
		self.window.tableViewPositions.resizeColumnsToContents()
		self.window.tableViewPositions.viewport().update()

	def disconnect(self):
		if self.client_ws is not None:
			self.client_ws.close()
			self.client_ws = None
		self.account.clear()

	def fetch(self):
		curr = self.window.comboCurr.currentText()
		pctStrike = self.window.spinBoxStrikePercent.value() / 100.0
		minExpiry = self.window.spinBoxMinExpiry.value()
		maxExpiry = self.window.spinBoxMaxExpiry.value()
		idxPrice = self.client_rest.getindex(curr)
		self.fetchInstruments(curr, idxPrice[curr], pctStrike, minExpiry, maxExpiry)

	def fetchInstruments(self, curr, idxPrice, pctStrike, minExpiry, maxExpiry):
		instrs = self.client_rest.getinstruments(curr, "option")
		results = []
		minStrike = (1.0 - pctStrike) * idxPrice
		maxStrike = (1.0 + pctStrike) * idxPrice
		for instr in instrs:
			if instr['strike'] >= minStrike and instr['strike'] <= maxStrike:
				if instr['expiration_timestamp'] >= minExpiry and instr['expiration_timestamp'] <= maxExpiry:
					print(instr['instrument_name'])

	


		