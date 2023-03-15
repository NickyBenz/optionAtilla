
class AccountData:
	def __init__(self):
		self.currency = None
		self.equity = 0
		self.projectedInitialMargin = 0
		self.projectedMaintenanceMargin = 0
		self.availableMargin = 0
		self.initialMargin = 0
		self.maintenanceMargin = 0
		self.withdrawableFunds = 0
		self.PnL = 0
		self.delta = 0
		self.gamma = 0
		self.vega = 0
		self.theta = 0
		self.rows = 13
		self.cols = 2
	
	def clear(self):
		self.currency = ""
		self.equity = 0
		self.projectedInitialMargin = 0
		self.projectedMaintenanceMargin = 0
		self.availableMargin = 0
		self.initialMargin = 0
		self.maintenanceMargin = 0
		self.withdrawableFunds = 0
		self.PnL = 0
		self.delta = 0
		self.gamma = 0
		self.vega = 0
		self.theta = 0
		self.rows = 13
		self.cols = 2

	def update(self, dict_obj):
		print(dict_obj)
		self.currency = dict_obj['currency']
		self.equity = dict_obj["equity"]
		self.projectedInitialMargin = dict_obj["projected_initial_margin"]
		self.projectedMaintenanceMargin = dict_obj["projected_maintenance_margin"]
		self.availableMargin = dict_obj["margin_balance"]
		self.initialMargin = dict_obj["initial_margin"]
		self.maintenanceMargin = dict_obj["maintenance_margin"]
		self.withdrawableFunds = dict_obj["available_withdrawal_funds"]
		self.PnL = dict_obj["total_pl"]
		self.delta = dict_obj["options_delta"]
		self.gamma = dict_obj["options_gamma"]
		self.vega = dict_obj["options_vega"]
		self.theta = dict_obj["options_theta"]
		
	def getRows(self):
		return self.rows
		
	def getCols(self):
		return self.cols
		
	def getData(self, i, j):
		if j == 0:
			if i == 0:
				return "Currency"
			elif i == 1:
				return "Equity"
			elif i == 2:
				return "p_init_margin"
			elif i == 3:
				return "p_mnt_margin"
			elif i == 4:
				return "margin_bal"
			elif i == 5:
				return "init_margin"
			elif i == 6:
				return "mnt_margin"
			elif i == 7:
				return "avlble_funds"
			elif i == 8:
				return "PnL"
			elif i == 9:
				return "Delta"
			elif i == 10:
				return "Gamma"
			elif i == 11:
				return "Vega"
			elif i == 12:
				return "Theta"
			else:
				return ""
		else:
			if i == 0:
				return self.currency
			elif i == 1:
				return self.equity
			elif i == 2:
				return self.projectedInitialMargin
			elif i == 3:
				return self.projectedMaintenanceMargin
			elif i == 4:
				return self.availableMargin
			elif i == 5:
				return self.initialMargin
			elif i == 6:
				return self.maintenanceMargin
			elif i == 7:
				return self.withdrawableFunds
			elif i == 8:
				return self.PnL
			elif i == 9:
				return self.delta
			elif i == 10:
				return self.gamma
			elif i == 11:
				return self.vega
			elif i == 12:
				return self.theta
			else:
				return 0