from account_data import AccountData

class Atilla:
	def __init__(self, config_file):
		self.cfg = configparser.ConfigParser()
        self.cfg.read(config_file)
        self.currency = None
		self.account = AccountData()
	
	def connect(currency, prod=False):
		
		