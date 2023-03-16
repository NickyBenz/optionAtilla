
class SelectionData:
	def __init__(self):
		self.positions = []
		self.cols = 6
	
	def clear(self):
		self.positions = []
		self.cols = 6

	def update(self, positions):
		self.positions = positions
		
	def getRows(self):
		return len(self.positions) + 1
		
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
			op = self.positions[j-1].op
			
			if i == 0:
				return op.name
			elif i == 1:
				return self.positions[j-1].size
			elif i == 2:
				return op.bid_amount
			elif i == 3:
				return op.bid_price
			elif i == 4:
				return op.ask_price
			elif i == 5:
				return op.ask_amount
			else:
				return 0