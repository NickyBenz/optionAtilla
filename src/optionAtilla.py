import configparser
from collections import namedtuple
from datetime import datetime as dt
from account_data import AccountData
from position_data import PositionData
from selection_data import SelectionData
from account_model import AccountModel
from position_model import PositionModel
from selection_model import SelectionModel
from deribit_rest import RestClient
from deribit_ws import Deribit_WS
from PyQt6 import QtCore

Option = namedtuple('Option', ['name', 'kind', 'expiry', 'strike', 'delta', 'gamma', 'vega', 'theta', 
			       'bid_price', 'bid_amount', 'ask_price', 'ask_amount', 'size'])

class Atilla(QtCore.QObject):
	def __init__(self, parent, config_file):
		super().__init__(parent)
		self.parent = parent
		self.currency = None
		self.counter = 0
		self.subscriptions = 0
		self.market_cache = {}
		self.account = AccountData()
		self.positions = PositionData()
		self.selections = SelectionData()
		self.account_model = AccountModel(parent)
		self.position_model = PositionModel(parent)
		self.selection_model = SelectionModel(parent)

		self.account_model.update(self.account)
		self.position_model.update(self.positions)
		self.selection_model.update(self.selections)
		
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
		self.disconnect()
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


	def onMarketData(self, mkt_data):
		instr = mkt_data['instrument_name']
		now = dt.today()

		if instr not in self.market_cache:
			expiry = self.timestamp_to_datetime(mkt_data['expiration_timestamp'])
			greeks = mkt_data['greeks']
			self.market_cache[instr] = 	Option(instr, 
		                        				1 if mkt_data['option_type'] == 'call' else -1,
												(expiry - now).days, mkt_data['strike'], 
												greeks['delta'], greeks['gamma'], greeks['vega'], greeks['theta'],
												mkt_data['best_bid_price'], mkt_data['best_bid_amount'],
												mkt_data['best_ask_price'], mkt_data['best_ask_amount'], 0)
		else:
			greeks = mkt_data['greeks']
			self.market_cache[instr]._replace(delta = greeks['delta'], gamma = greeks['gamma'], vega=greeks['vega'], theta = greeks['theta'],
				                              bid_price = mkt_data['best_bid_price'], bid_amount = mkt_data['best_bid_amount'],
											  ask_price = mkt_data['best_ask_price'], ask_amount = mkt_data['best_ask_amount'])
		
		
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
			self.client_ws.disconnect()
			self.client_ws.close()
			self.client_ws = None

		self.account_model.beginResetModel()
		self.position_model.beginResetModel()
		self.selection_model.beginResetModel()
		self.account.clear()
		self.positions.clear()
		self.market_cache.clear()
		self.account_model.endResetModel()
		self.position_model.endResetModel()
		self.selection_model.endResetModel()
		self.counter = 0
		self.subscriptions = 0


	def fetch(self):
		
		curr = self.window.comboCurr.currentText()
		pctStrike = self.window.spinBoxStrikePercent.value() / 100.0
		minExpiry = self.window.spinBoxMinExpiry.value()
		maxExpiry = self.window.spinBoxMaxExpiry.value()
		idxPrice = self.client_rest.getindex(curr)

		for pos in self.positions.positions:
			if pos['instrument_name'] not in self.market_cache:
				self.client_ws.ticker(pos['instrument_name'])

		self.counter = self.fetchInstruments(curr, idxPrice[curr], pctStrike, minExpiry, maxExpiry) + len(self.positions.positions)


	def timestamp_to_datetime(self, timestamp): 
		return dt.fromtimestamp(timestamp/1000)


	def fetchInstruments(self, curr, idxPrice, pctStrike, minExpiry, maxExpiry):
		instrs = self.client_rest.getinstruments(curr, "option")
		minStrike = (1.0 - pctStrike) * idxPrice
		maxStrike = (1.0 + pctStrike) * idxPrice
		now = dt.today()
		counter = 0

		for instr in instrs:
			if instr['strike'] >= minStrike and instr['strike'] <= maxStrike:
				expiry = instr['expiration_timestamp']
				days_left = (self.timestamp_to_datetime(expiry) - now).days

				if days_left >= minExpiry and days_left <= maxExpiry:
					counter += 1
					self.client_ws.ticker(instr['instrument_name'])

		return counter