from abc import ABC, abstractmethod
import numpy as np


class PhysicsConstants:
    Alpha = 1 / 137.036
    Gev2ToNb = 389379.366


class FourVector:

    def __init__(self, eVal, pxVal, pyVal, pzVal):
        self.eVal = eVal
        self.pxVal = pxVal
        self.pyVal = pyVal
        self.pzVal = pzVal

    def __repr__(self):
        return f"(E: {self.eVal:6.2f}, px: {self.pxVal:6.2f}, py: {self.pyVal:6.2f}, pz: {self.pzVal:6.2f})"


class Particle:

    def __init__(self, pdgId, p4, mother=None, eventId=None):
        self.pdgId = pdgId
        self.p4 = p4
        self.mother = mother
        self.eventId = eventId

    def __str__(self):
        motherStr = self.mother if self.mother else "Initial Beam"
        return f"Event {self.eventId:03d} | PDG: {self.pdgId:>3} | Mother: {motherStr:<12} | P4: {self.p4}"


# --- The "Interface" Class ---

class IProcess(ABC):

    @abstractmethod
    def GetMaxWeight(self):
        pass

    @abstractmethod
    def DifferentialCrossSection(self, cosTheta):
        pass

    @abstractmethod
    def TotalCrossSection(self):
        pass

    @property
    @abstractmethod
    def PdgetIn(self):
        pass

    @property
    @abstractmethod
    def PdgetOut(self):
        pass


# --- Implementing the Interface ---

class MuonToElectron(IProcess):

    def __init__(self, sqrtS):
        self.sqrtS = sqrtS
        self.sVal = sqrtS ** 2
        self.processName = "mu+ mu- -> e+ e-"
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

class QedSimulation:
    def __init__(self, activeProcess):
        self.activeProcess = activeProcess
        self.eventList = []

    def SampleCosTheta(self):
        maxW = self.activeProcess.GetMaxWeight()
        while True:
            c = np.random.uniform(-1, 1)
            if np.random.uniform(0, maxW) <= self.activeProcess.DifferentialCrossSection(c):
                return c

    def Run(self, nEvents):
        print(f"{'=' * 90}\nSTARTING SIMULATION: {self.activeProcess.processName}")
        print(f"Total Cross Section: {self.activeProcess.TotalCrossSection():.6f} nb\n{'=' * 90}")

        for i in range(1, nEvents + 1):
            eBeam = self.activeProcess.sqrtS / 2.0

            muMinus = Particle(self.activeProcess.PdgetIn[0], FourVector(eBeam, 0, 0, eBeam), eventId=i)
            muPlus = Particle(self.activeProcess.PdgetIn[1], FourVector(eBeam, 0, 0, -eBeam), eventId=i)

            cosTheta = self.SampleCosTheta()
            phiVal = np.random.uniform(0, 2 * np.pi)
            sinTheta = np.sqrt(1 - cosTheta ** 2)

            px = eBeam * sinTheta * np.cos(phiVal)
            py = eBeam * sinTheta * np.sin(phiVal)
            pz = eBeam * cosTheta

            p1 = Particle(self.activeProcess.PdgetOut[0], FourVector(eBeam, px, py, pz), mother="Collision", eventId=i)
            p2 = Particle(self.activeProcess.PdgetOut[1], FourVector(eBeam, -px, -py, -pz), mother="Collision",
                          eventId=i)

            self.eventList.append([muMinus, muPlus, p1, p2])
            for p in self.eventList[-1]: print(p)
            print("-" * 90)


if __name__ == "__main__":
    myProcess = MuonToElectron(sqrtS=91.18)
    generator = QedSimulation(myProcess)
    generator.Run(nEvents=5)