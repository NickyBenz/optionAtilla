
class SelectionData:
	def __init__(self):
		self.options = []
		self.cols = 6
	
	def clear(self):
		self.options = []
		self.cols = 6

	def update(self, opts):
		self.options = opts
		
	def getRows(self):
		return len(self.options) + 1
		
	def getCols(self):
		return self.cols
		
	def getData(self, j, i):
		if j == 0:
			if i == 0:
				return "Instr"
			elif i == 1:
				return "Size"
			elif i == 2:
				return "BidAmount"
			elif i == 3:
				return "BidPrice"
			elif i == 4:
				return "AskPrice"
			elif i == 5:
				return "AskAmount"
			else:
				return ""
		else:
			op = self.options[j-1]
			
			if i == 0:
				return op.name
			elif i == 1:
				return op.size
			elif i == 2:
				return op['bid_amount']
			elif i == 3:
				return op['bid_price']
			elif i == 4:
				return op['ask_price']
			elif i == 5:
				return op['ask_amount']
			else:
				return 0