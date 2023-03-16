import configparser
from datetime import datetime as dt
import opstrat
from account_data import AccountData
from image_viewer import ImageViewer
from position_data import PositionData
from selection_data import SelectionData
from account_model import AccountModel
from optimise_params import OptimiseParams
from optimizer import Optimizer
from deribit_option import Option
from deribit_option_position import DeribitPosition
from position_model import PositionModel
from selection_model import SelectionModel
from deribit_rest import RestClient
from deribit_ws import Deribit_WS
from PyQt6 import QtCore

class Atilla(QtCore.QObject):
	def __init__(self, parent, config_file):
		super().__init__(parent)
		self.parent = parent
		self.currency = None
		self.counter = 0
		self.subscriptions = 0
		self.subscribed = set()
		self.market_cache = {}
		self.fetches = []
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
		self.mainW = None


	def setWindow(self, window, mainW):
		self.window = window
		self.mainW = mainW
		self.window.tableViewAccount.setModel(self.account_model)
		self.window.tableViewPositions.setModel(self.position_model)
		self.window.pushButtonConnect.clicked.connect(self.connect)
		self.window.pushButtonClose.clicked.connect(self.close)
		self.window.pushButtonFetch.clicked.connect(self.fetch)
		self.window.pushButtonPositions.clicked.connect(self.queryPos)
		self.window.pushButtonDisplay.clicked.connect(self.display)
		self.window.pushButtonCompute.clicked.connect(self.compute)
		QtCore.QMetaObject.connectSlotsByName(self)
	

	def close(self):
		self.disconnect()
		self.window.centralwidget.close()

	def authenticate(self):
		self.client_ws.authenticate()
		print("sent authenticate request")

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
		self.client_ws = Deribit_WS(self.parent)
		self.client_ws.connect(self, api_key, api_secret, ws_url)
		QtCore.QTimer.singleShot(3000, self.authenticate)
		QtCore.QTimer.singleShot(6000, self.getChanges)


	def onMarketData(self, mkt_data):
		instr = mkt_data['instrument_name']

		if instr not in self.subscribed:
			self.subscribed.add(instr)
			self.window.progressBarFetch.setVisible(False)
			self.window.progressBarFetch.setValue(len(self.subscribed) * 100.0 / self.counter)
			self.window.progressBarFetch.setVisible(True)

		greeks = mkt_data['greeks']
		opt = self.market_cache[instr]
		opt.delta = greeks['delta']
		opt.gamma = greeks['gamma'] 
		opt.vega=greeks['vega']
		opt.theta = greeks['theta']
		opt.bid_price = mkt_data['best_bid_price']
		opt.bid_amount = mkt_data['best_bid_amount']
		opt.ask_price = mkt_data['best_ask_price']
		opt.ask_amount = mkt_data['best_ask_amount']
		self.window.tableViewPositions.viewport().update()
		self.window.tableViewSelections.viewport().update()
		
	def onAccountData(self, dict_obj):
		self.account.update(dict_obj)
		self.window.tableViewAccount.viewport().update()

	def onPositionCreate(self, positions):
		self.position_model.beginResetModel()
		self.positions.add(positions)
		self.position_model.endResetModel()
		self.window.tableViewPositions.resizeColumnsToContents()
		self.window.tableViewPositions.viewport().update()


	def onPositionData(self, positions):
		self.positions.update(positions)
		self.window.tableViewPositions.viewport().update()

	def disconnect(self):
		if self.client_ws is not None:
			self.client_ws.close()
			self.client_ws = None

		self.account_model.beginResetModel()
		self.position_model.beginResetModel()
		self.selection_model.beginResetModel()
		self.account.clear()
		self.positions.clear()
		self.market_cache.clear()
		self.subscribed.clear()
		self.account_model.endResetModel()
		self.position_model.endResetModel()
		self.selection_model.endResetModel()
		self.counter = 0
		self.subscriptions = 0
		self.fetches = []

	def queryPos(self):
		curr = self.window.comboCurr.currentText()
		positions = self.client_rest.getpositions(curr, "option")
		now = dt.today()
		results = []
		for pos in positions:
			name = pos['instrument_name']
			instr = self.client_rest.getinstrument(name)
			expiry = self.timestamp_to_datetime(instr['expiration_timestamp'])
			days_left = (expiry - now).days
			size = pos['size']
			opt = Option(name, instr['option_type'], days_left, instr['strike'], 
		                 pos['delta'] / size,pos['gamma'] / size,pos['vega'] / size, pos['theta'] / size,0,0,0,0)
			dpos = DeribitPosition(opt, pos['size'])
			results.append(dpos)
			if name not in self.market_cache.keys():
				self.market_cache[name] = opt
				self.counter += 1
				QtCore.QThread.msleep(100)
				self.client_ws.ticker(name)
		self.onPositionCreate(results)

	def fetch(self):
		self.fetches = []
		curr = self.window.comboCurr.currentText()
		pctStrike = self.window.spinBoxStrikePercent.value() / 100.0
		minExpiry = self.window.spinBoxMinExpiry.value()
		maxExpiry = self.window.spinBoxMaxExpiry.value()
		idxPrice = self.client_rest.getindex(curr)
		now = dt.today()
		self.queryPos()
		self.fetchInstruments(now, curr, idxPrice[curr], pctStrike, minExpiry, maxExpiry)
		self.window.progressBarFetch.setValue(len(self.subscribed) * 100.0 / self.counter)


	def timestamp_to_datetime(self, timestamp): 
		return dt.fromtimestamp(timestamp/1000)


	def fetchInstruments(self, now, curr, idxPrice, pctStrike, minExpiry, maxExpiry):
		instrs = self.client_rest.getinstruments(curr, "option")
		minStrike = (1.0 - pctStrike) * idxPrice
		maxStrike = (1.0 + pctStrike) * idxPrice

		for instr in instrs:
			if instr['strike'] >= minStrike and instr['strike'] <= maxStrike:
				expiry = instr['expiration_timestamp']
				days_left = (self.timestamp_to_datetime(expiry) - now).days

				if days_left >= minExpiry and days_left <= maxExpiry:
					name = instr['instrument_name']
					if name not in self.market_cache.keys():
						self.market_cache[name] = Option(name, instr['option_type'], days_left,
					                                      instr['strike'], 0,0,0,0,0,0,0,0)
						self.counter += 1
						QtCore.QThread.msleep(300)
						self.client_ws.ticker(name)
						self.fetches.append(self.market_cache[name])

	def display(self):
		positions = self.positions.positions
		oplist = []

		for pos in positions:
			op = {'op_type': pos.kind[0],
            		'strike': pos.strike,
            		'tr_type': 'b' if pos.size > 0 else 's',
            		'op_pr': pos.bid_price if pos.size < 0 else pos.ask_price,
            		'contract': abs(pos.size)}
			oplist.append(op)

		for pos in self.fetches:
			op = {'op_type': pos.kind[0],
            		'strike': pos.strike,
            		'tr_type': 'b' if pos.size > 0 else 's',
            		'op_pr': pos.bid_price if pos.size < 0 else pos.ask_price,
            		'contract': 2}
			oplist.append(op)
			break

		curr = self.window.comboCurr.currentText()
		idx_price = self.client_rest.getindex(curr)[curr]
		opstrat.multi_plotter(spot=idx_price, spot_range=20, op_list=oplist, save=True, file='file.png')
		viewer = ImageViewer()
		viewer.update()
		viewer.show()
		viewer.deleteLater()

	def create_optimiser_params(self):
		curr = self.window.comboCurr.currentText()
		params = OptimiseParams.create_default()
		
		if curr == 'BTC':
			params.contract_size = 0.1
		else:
			params.contract_size = 1

		params.currObjective = self.window.comboObjective.currentText()
		params.maxDeltaPct = self.window.spinDelta.value() / 100.0
		params.minGammaBps = self.window.spinGamma.value() / 10000.0
		params.minTheta = self.window.spinMinTheta.value()
		params.positiveVega = self.window.checkVega.isChecked()
		params.putNeutral = self.window.checkPutNeutral.isChecked()
		params.callNeutral = self.window.checkCallNeutral.isChecked()
		params.longPut = self.window.checkLongPut.isChecked()
		params.longCall = self.window.checkLongCall.isChecked()
		params.usePositions = self.window.checkPositions.isChecked()
		params.maxUnit = self.window.spinMaxUnit.value()
		params.maxTotal = self.window.spinMaxTotal.value()
		params.maxSpreadBps = self.window.spinBoxSpread.value() / 10000.0
		params.doubleFee = self.window.checkDoubleFee.isChecked()
		return params

	def compute(self):
		params = self.create_optimiser_params()
		optim = Optimizer(params, self.fetches, self.positions.positions)
		optim.compute()
