import numpy as np
from Particle import Particle
from FourVector import FourVector
from pathlib import Path


class Event:
    """
    A container for a single collision 'snapshot'.
    It stores the 'Initial State' (particles going in) and
    the 'Final State' (particles coming out).
    """

    def __init__(self, id, initialParticles, finalParticles):
        self.id = id
        self.initialParticles = initialParticles
        self.finalParticles = finalParticles


class QedSimulation:
    """
    The main simulation engine. It uses Monte Carlo methods to
    simulate particle scattering based on Quantum Electrodynamics (QED).
    """

    def __init__(self, activeProcess, particleRegistry):
        self.activeProcess = activeProcess
        self.particleRegistry = particleRegistry
        self.eventList = []

    def SampleCosTheta(self):
        """
        Uses the 'Acceptance-Rejection' method to determine the scattering angle.
        It generates random candidates and keeps them only if they
        match the probability distribution of the physics process.
        """
        maxWeight = self.activeProcess.GetMaxWeight()
        while True:
            # Pick a random candidate for the cosine of the angle
            cosineCandidate = np.random.uniform(-1, 1)
            # Pick a random vertical value to check against the physics curve
            checkValue = np.random.uniform(0, maxWeight)

            # If the value is below the Differential Cross Section curve, accept it.
            if checkValue <= self.activeProcess.DifferentialCrossSection(cosineCandidate):
                return cosineCandidate

    def SerializeEvent(self, event):
        """
        Converts the Event data into a formatted string that
        matches the project's internal text format.
        """
        lines = []
        lines.append(f"Event {event.id}")

        for particle in event.initialParticles:
            lines.append(f"    {particle}")

        for particle in event.finalParticles:
            lines.append(f"    {particle}")

        return "\n".join(lines)

    def WriteOutput(self, outFile):
        """
        Saves all generated events into a text file within the 'outputs' directory.
        """
        projectRoot = Path(__file__).resolve().parent.parent
        outputPath = projectRoot / "outputs" / outFile
        outputPath.parent.mkdir(parents=True, exist_ok=True)

        with open(outputPath, "w") as file:
            for event in self.eventList:
                serialized = self.SerializeEvent(event)
                file.write(serialized + "\n\n")

        print(f"\nOutput written to: {outputPath}")

    def Run(self, nEvents, outFile):
        """
        The main execution loop. It creates the incoming beams,
        calculates the collision results, and stores the events.
        """
        print("=" * 90)
        print(f"STARTING SIMULATION: {self.activeProcess.processName}")
        print(f"Total Cross Section: {self.activeProcess.TotalCrossSection():.6f} nb")
        print("=" * 90)

        # Retrieve particle definitions (mass, charge, etc.) from the registry
        muonType = self.particleRegistry.GetByPdg(self.activeProcess.PdgetIn[0])
        antiMuonType = self.particleRegistry.GetByPdg(self.activeProcess.PdgetIn[1])
        electronType = self.particleRegistry.GetByPdg(self.activeProcess.PdgetOut[0])
        positronType = self.particleRegistry.GetByPdg(self.activeProcess.PdgetOut[1])

        for i in range(nEvents):
            # Calculate beam energy (E = sqrt(s) / 2)
            energyBeam = self.activeProcess.sqrtS / 2.0

            # Define initial particles flying along the Z-axis in opposite directions
            muMinus = Particle(muonType, FourVector(energyBeam, 0, 0, energyBeam), eventID=i)
            muPlus = Particle(antiMuonType, FourVector(energyBeam, 0, 0, -energyBeam), eventID=i)

            # Determine the outgoing trajectory using random sampling
            cosTheta = self.SampleCosTheta()
            phiVal = np.random.uniform(0, 2 * np.pi)  # Azimuthal angle (rotation around the beam)
            sinTheta = np.sqrt(1 - cosTheta ** 2)

            # Convert angles into 3D momentum components (px, py, pz)
            pxVal = energyBeam * sinTheta * np.cos(phiVal)
            pyVal = energyBeam * sinTheta * np.sin(phiVal)
            pzVal = energyBeam * cosTheta

            # Create the 'Final State' particles (Electron and Positron)
            # They are emitted 'back-to-back' to conserve total momentum.
            p1 = Particle(
                electronType,
                FourVector(energyBeam, pxVal, pyVal, pzVal),
                mother="Collision",
                eventID=i
            )

            p2 = Particle(
                positronType,
                FourVector(energyBeam, -pxVal, -pyVal, -pzVal),
                mother="Collision",
                eventID=i
            )

            # Group the results into an Event and add it to the list
            event = Event(i, [muMinus, muPlus], [p1, p2])
            self.eventList.append(event)

        # Print results to the console for verification
        for event in self.eventList:
            print(self.SerializeEvent(event))
            print("-" * 90)

        self.WriteOutput(outFile)