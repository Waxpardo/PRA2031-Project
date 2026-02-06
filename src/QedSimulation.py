import numpy as np
from Particle import Particle
from FourVector import FourVector

class QedSimulation:
    def __init__(self, activeProcess, particleRegistry):
        self.activeProcess = activeProcess
        self.particleRegistry = particleRegistry
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

        # Pre-fetch ParticleType objects from registry using PDG IDs
        muonType = self.particleRegistry.GetByPdg(self.activeProcess.PdgetIn[0])
        antiMuonType = self.particleRegistry.GetByPdg(self.activeProcess.PdgetIn[1])
        electronType = self.particleRegistry.GetByPdg(self.activeProcess.PdgetOut[0])
        positronType = self.particleRegistry.GetByPdg(self.activeProcess.PdgetOut[1])

        for i in range(1, nEvents + 1):
            eBeam = self.activeProcess.sqrtS / 2.0

            # Initial state
            muMinus = Particle(muonType, FourVector(eBeam, 0, 0, eBeam), eventID=i)
            muPlus = Particle(antiMuonType, FourVector(eBeam, 0, 0, -eBeam), eventID=i)

            # Sampling
            cosTheta = self.SampleCosTheta()
            phiVal = np.random.uniform(0, 2 * np.pi)
            sinTheta = np.sqrt(1 - cosTheta ** 2)

            # Final state kinematics
            px = eBeam * sinTheta * np.cos(phiVal)
            py = eBeam * sinTheta * np.sin(phiVal)
            pz = eBeam * cosTheta

            p1 = Particle(electronType, FourVector(eBeam, px, py, pz), mother="Collision", eventID=i)
            p2 = Particle(positronType, FourVector(eBeam, -px, -py, -pz), mother="Collision", eventID=i)

            self.eventList.append([muMinus, muPlus, p1, p2])
            for p in self.eventList[-1]: print(p)
            print("-" * 90)