
class AccountData:
	def __init__(self):
		self.currency = None
		self.equity = 0
		self.equityDollar = 0
		self.availableMargin = 0
		self.initialMargin = 0
		self.maintenanceMargin = 0
		self.PnL = 0
		self.rows = 7
		self.cols = 2
		
	def update(self, curr, equity, equityDollar, availableMargin, initialMargin, maintenanceMargin, pnl):
		self.currency = curr
		self.equity = equity
		self.equityDollar = equity
		self.availableMargin = availableMargin
		self.initialMargin = initialMargin
		self.maintenanceMargin = maintenanceMargin
		self.PnL = pnl
		
	def getRows(self):
		return self.rows
		
	def getCols(self):
		return self.cols
		
	def getData(i, j):
		if j == 0:
			return headers[i]
		else:
			if i == 0:
				return self.currency
			elif i == 1:
				return self.equity
			elif i == 2:
				return self.equityDollar
			elif i == 3:
				return self.availableMargin
			elif i == 4:
				return self.initialMargin
			elif i == 5:
				return self.maintenanceMargin
			elif i == 6:
				return self.PnL
			else:
				return 0