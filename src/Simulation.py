import numpy as np
class PhysicsConstants:
    ALPHA = 1 / 137.036  # Fine-structure constant
    # (hbar * c)^2 approx 389379.366 GeV^2 * nb
    GEV2_TO_NB = 389379.366


class FourVector:
    def __init__(self, E, px, py, pz):
        self.E = E
        self.px = px
        self.py = py
        self.pz = pz

    def __repr__(self):
        return f"(E: {self.E:6.2f}, px: {self.px:6.2f}, py: {self.py:6.2f}, pz: {self.pz:6.2f})"


class Particle:

    def __init__(self, pdgId, p4, mother=None, eventId=None):
        self.pdgId = pdgId  # 13: mu-, -13: mu+, 11: e-, -11: e+
        self.p4 = p4  # Reference to a FourVector instance
        self.mother = mother  # Track where the particle came from
        self.eventId = eventId

    def __str__(self):
        mother_str = self.mother if self.mother else "Initial Beam"
        return (f"Event {self.eventId:03d} | PDG: {self.pdgId:>3} | "
                f"Mother: {mother_str:<12} | P4: {self.p4}")


class QEDSimulation:
    """
    Monte Carlo Generator for mu+ mu- -> e+ e-.
    """

    def __init__(self, sqrtS):
        self.sqrtS = sqrtS
        self.s = sqrtS ** 2
        self.events = []

    def CalculateTotalCrossSection(self):
        """
        Formula: sigma = (4 * pi * alpha^2) / (3 * s)
        """
        sigmaNatural = (4 * np.pi * PhysicsConstants.ALPHA ** 2) / (3 * self.s)
        sigmaNb = sigmaNatural * PhysicsConstants.GEV2_TO_NB
        return sigmaNb

    def SampleCosTheta(self):
        """Samples the 1 + cos^2(theta) angular distribution."""
        while True:
            cosTheta = np.random.uniform(-1, 1)
            weight = np.random.uniform(0, 2)
            if weight <= (1 + cosTheta ** 2):
                return cosTheta

    def Run(self, nEvents):
        """Executes the simulation and prints the event logs."""
        totalSigma = self.CalculateTotalCrossSection()

        print(f"{'=' * 90}")
        print(f"Process: mu+ mu- -> e+ e-")
        print(f"Center of Mass Energy (sqrt_s): {self.sqrtS} GeV")
        print(f"Theoretical Total Cross Section: {totalSigma:.6f} nb")
        print(f"{'=' * 90}\n")

        for i in range(1, nEvents + 1):
            eBeam = self.sqrtS / 2.0

            # --- 1. Initial State: Incoming Muons ---
            p4MuMinus = FourVector(eBeam, 0, 0, eBeam)
            p4MuPlus = FourVector(eBeam, 0, 0, -eBeam)

            muMinus = Particle(13, p4MuMinus, mother=None, eventId=i)
            muPlus = Particle(-13, p4MuPlus, mother=None, eventId=i)

            # --- 2. Interaction: Sampling scattering angles ---
            cosTheta = self.SampleCosTheta()
            phi = np.random.uniform(0, 2 * np.pi)
            sinTheta = np.sqrt(1 - cosTheta ** 2)

            # --- 3. Final State: Outgoing Electrons ---
            px = eBeam * sinTheta * np.cos(phi)
            py = eBeam * sinTheta * np.sin(phi)
            pz = eBeam * cosTheta

            p4EMinus = FourVector(eBeam, px, py, pz)
            p4EPlus = FourVector(eBeam, -px, -py, -pz)  # Conservation of momentum

            eMinus = Particle(11, p4EMinus, mother="mu+ mu-", eventId=i)
            ePlus = Particle(-11, p4EPlus, mother="mu+ mu-", eventId=i)

            # Store and Print the event log
            eventSnapshot = [muMinus, muPlus, eMinus, ePlus]
            self.events.append(eventSnapshot)

            for p in eventSnapshot:
                print(p)
            print("-" * 90)


# --- Main Entry Point ---
if __name__ == "__main__":
    simulation = QEDSimulation(sqrtS=91.18)
    simulation.Run(nEvents=5)