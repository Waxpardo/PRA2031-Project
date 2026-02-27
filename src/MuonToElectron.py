import numpy as np
from Process import Process
from PhysicsConstants import PhysicsConstants


class MuonToElectron(Process):
    """
    Defines the physics for mu+ mu- -> e+ e-.
    This is a classic 'Lepton Scattering' process where two heavy leptons (muons)
    annihilate and transform into two lighter leptons (electrons).
    """

    def __init__(self, sqrtS):
        # sqrtS is the total energy available in the collision center.
        self.sqrtS = sqrtS
        # 's' is the square of the energy, a standard variable in particle physics math.
        self.sVal = sqrtS ** 2
        self.processName = "mu+ mu- -> e+ e-"

        # PDG codes: 13 is Muon, -13 is Antimuon. 11 is Electron, -11 is Positron.
        self.pdgIn = [13, -13]
        self.pdgOut = [11, -11]

    @property
    def PdgetIn(self):
        return self.pdgIn

    @property
    def PdgetOut(self):
        return self.pdgOut

    def GetMaxWeight(self):
        """
        Used for the 'Acceptance-Rejection' sampling method.
        Since the maximum value of (1 + cos^2(theta)) is 2, we set this as the ceiling.
        """
        return 2.0

    def DifferentialCrossSection(self, cosTheta):
        """
        Describes the 'shape' of the scattering.
        For this QED process, the particles prefer to fly out either
        straight forward or straight backward rather than at 90 degrees.
        """
        # The (1 + cos^2) distribution is the signature of spin-1/2 particle scattering.
        return 1 + cosTheta ** 2

    def TotalCrossSection(self):
        """
        Calculates the actual probability (area) of this collision happening.
        The result is converted into 'nanobarns' (nb), a standard unit of area in physics.
        """
        # alpha is the Fine Structure Constant (~1/137), describing the strength of EM force.
        sigmaNatural = (4 * np.pi * PhysicsConstants.Alpha ** 2) / (3 * self.sVal)

        # Gev2ToNb converts the 'natural' units used in math to measurable 'barns'.
        return sigmaNatural * PhysicsConstants.Gev2ToNb