import math 
class Particle:
    """A class to define the Mother particle"""
    
    def __init__(self, name, PDG, mass, charge, px, py, pz):
        self.name = name
        self.PDG = PDG
        self.mass = mass
        self.charge = charge
        self.px = px
        self.py = py
        self.pz = pz
        self.energy = self.calcEnergy()
    
    def pTotal(self):
        return math.sqrt(self.px**2 + self.py**2 + self.pz**2)
    
    def pTransverse(self):
        return math.sqrt(self.px**2 + self.py**2)
    
    def eta(self):
        pTot = self.pTotal()
        if pTot != abs(self.pz):
            return 0.5 * math.log((pTot + self.pz) / (pTot - self.pz))
        else:
            return float('inf')

    def aziAngle(self):
        return math.atan2(self.py, self.px)
    
    def calcEnergy(self):
        p = self.pTotal()
        return math.sqrt(p**2 + self.mass**2)
    
    def print_info(self):
        print(f"Mother Particle: {self.name} (PDG {self.PDG})")
        print(f"Mass: {self.mass} GeV, Charge: {self.charge}")
        print(f"Momentum: ({self.px}, {self.py}, {self.pz}) GeV")
        print(f"p_total: {self.pTotal():.2f}, pT: {self.pTransverse():.2f}")
        print(f"Pseudorapidity: {self.eta():.2f}, Phi: {self.aziAngle():.2f}")



kaon = Particle("Kaon+", 321, 0.4937, +1, 0.3, 0.4, 1.2, )

kaon.print_info()

