from PyQt6 import QtCore
from account_data import AccountData

class AccountModel(QtCore.QAbstractTableModel): 
    def __init__(self, parent=None, *args): 
        super(AccountModel, self).__init__()
        self.accountData = None

        
    def update(self, accountData):
        self.accountData = accountData
        
     
    def rowCount(self, parent=QtCore.QModelIndex()):
        return self.accountData.getRows()

        
    def columnCount(self, parent=QtCore.QModelIndex()):
        return self.accountData.getCols()

        
    def data(self, index, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole and self.accountData is not None:
            i = index.row()
            j = index.column()
            return '{0}'.format(self.accountData.getData(i, j))
        else:
            return QtCore.QVariant()