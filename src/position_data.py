
class PositionData:
	def __init__(self):
		self.positions = []
		self.cols = 6
	
	def clear(self):
		self.positions = []
		self.cols = 6

	def update(self, pos):
		self.positions = pos
		
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
				return "Delta"
			elif i == 3:
				return "Gamma"
			elif i == 4:
				return "Vega"
			elif i == 5:
				return "Theta"
			else:
				return ""
		else:
			pos = self.positions[j-1]
			
			if i == 0:
				return pos['instrument_name']
			elif i == 1:
				return pos['size']
			elif i == 2:
				return pos['delta']
			elif i == 3:
				return pos['gamma']
			elif i == 4:
				return pos['vega']
			elif i == 5:
				return pos['theta']
			else:
				return 0