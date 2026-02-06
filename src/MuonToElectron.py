import numpy as np
from Process import Process
from PhysicsConstants import PhysicsConstants
class MuonToElectron(Process):
    """Implementation of the mu+ mu- -> e+ e- process."""

    def __init__(self, sqrtS):
        self.sqrtS = sqrtS
        self.sVal = sqrtS ** 2
        self.processName = "mu+ mu- -> e+ e-"
        # Implementing property requirements
        self.pdgIn = [13, -13]
        self.pdgOut = [11, -11]

    @property
    def PdgetIn(self): return self.pdgIn

    @property
    def PdgetOut(self): return self.pdgOut

    def GetMaxWeight(self):
        return 2.0

    def DifferentialCrossSection(self, cosTheta):
        return 1 + cosTheta ** 2

    def TotalCrossSection(self):
        sigmaNatural = (4 * np.pi * PhysicsConstants.Alpha ** 2) / (3 * self.sVal)
        return sigmaNatural * PhysicsConstants.Gev2ToNb
