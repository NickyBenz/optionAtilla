class OptimiseParams:
    def __init__(self):
        self.minimize = True
        self.objectives = ["Min Cost", "Max Gamma", "Max Theta"]
        self.currObjective = 0
        self.maxDelta = 0.01
        self.minTheta = 5
        self.minGamma = 0.001
        self.putNeutral = True
        self.callNeutral = True
        self.positiveVega = True
        self.longPut = True
        self.longCall = True
        self.maxUnit = 5
        self.maxTotal = 15
        self.usePositions = True
        self.maxSpread = 0.001
        self.doubleFee = True

    @staticmethod
    def create_default():
        return OptimiseParams()