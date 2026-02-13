import numpy as np
from Particle import Particle
from FourVector import FourVector
from pathlib import Path

class Event:
    def __init__(self, id, initialParticles, finalParticles):
        self.id = id
        self.initialParticles = initialParticles
        self.finalParticles = finalParticles


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

    def SerializeEvent(self, event):
        lines = []
        lines.append(f"Event {event.id}")

        for particle in event.initialParticles:
            lines.append(f"    {particle}")

        for particle in event.finalParticles:
            lines.append(f"    {particle}")

        return "\n".join(lines)

    def WriteOutput(self, outFile):

        project_root = Path(__file__).resolve().parent.parent

        output_path = project_root / "outputs" / outFile

        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w") as file:
            for event in self.eventList:
                serialized = self.SerializeEvent(event)
                file.write(serialized + "\n\n")

        print(f"\nOutput written to: {output_path}")

    def Run(self, nEvents, outfile):

        print("=" * 90)
        print(f"STARTING SIMULATION: {self.activeProcess.processName}")
        print(f"Total Cross Section: {self.activeProcess.TotalCrossSection():.6f} nb")
        print("=" * 90)

        muonType = self.particleRegistry.GetByPdg(self.activeProcess.PdgetIn[0])
        antiMuonType = self.particleRegistry.GetByPdg(self.activeProcess.PdgetIn[1])
        electronType = self.particleRegistry.GetByPdg(self.activeProcess.PdgetOut[0])
        positronType = self.particleRegistry.GetByPdg(self.activeProcess.PdgetOut[1])

        for i in range(nEvents):

            eBeam = self.activeProcess.sqrtS / 2.0

            muMinus = Particle(muonType, FourVector(eBeam, 0, 0, eBeam), eventID=i)
            muPlus = Particle(antiMuonType, FourVector(eBeam, 0, 0, -eBeam), eventID=i)

            cosTheta = self.SampleCosTheta()
            phiVal = np.random.uniform(0, 2 * np.pi)
            sinTheta = np.sqrt(1 - cosTheta ** 2)

            px = eBeam * sinTheta * np.cos(phiVal)
            py = eBeam * sinTheta * np.sin(phiVal)
            pz = eBeam * cosTheta

            p1 = Particle(
                electronType,
                FourVector(eBeam, px, py, pz),
                mother="Collision",
                eventID=i
            )

            p2 = Particle(
                positronType,
                FourVector(eBeam, -px, -py, -pz),
                mother="Collision",
                eventID=i
            )

            event = Event(i, [muMinus, muPlus], [p1, p2])
            self.eventList.append(event)

        for event in self.eventList:
            print(self.SerializeEvent(event))
            print("-" * 90)

        self.WriteOutput(outfile)