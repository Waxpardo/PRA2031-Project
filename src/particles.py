class ParticleType:
    def __init__(self, name, pdg, type, mass, charge, stable, decay_modes):
        self.name = name
        self.pdg = pdg
        self.type = type
        self.mass = mass
        self.charge = charge
        self.stable = stable
        self.decay_modes = decay_modes

class Particle:
    def __init__(self, ParticleType, p, eta, phi, pt):
        self.ParticleType = ParticleType
        self.p = p
        self.eta = eta
        self.phi = phi
        self.pt = pt