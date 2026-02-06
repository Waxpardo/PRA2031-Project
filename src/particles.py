
import numpy as np
class ParticleType:
    def __init__(self, name, pdg, particle_type, mass, charge, stable, decay_modes):
        self.name = name
        self.pdg = pdg
        self.particle_type = particle_type
        self.mass = mass
        self.charge = charge
        self.stable = stable
        self.decay_modes = decay_modes
    
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        if not isinstance(name, str):
            raise TypeError("name must be a string")
        self._name = name
    
    @property
    def pdg(self):
        return self._pdg

    @pdg.setter
    def pdg(self, pdg):
        if not isinstance(pdg, int):
            raise TypeError("pdg must be an integer")
        self._pdg = pdg

    @property
    def particle_type(self):
        return self._particle_type

    @particle_type.setter
    def particle_type(self, particle_type):
        if not isinstance(particle_type, str):
            raise TypeError("particle_type must be a string")
        self._particle_type = particle_type

    @property
    def mass(self):
        if not isinstance(self._mass, float):
            raise TypeError("mass must be a float")
        return self._mass

    @mass.setter
    def mass(self, mass):
        self._mass = mass

    @property
    def charge(self):
        if not isinstance(self._charge, float):
            raise TypeError("charge must be a float")
        return self._charge

    @charge.setter
    def charge(self, charge):
        self._charge = charge

    @property
    def stable(self):
        return self._stable

    @stable.setter
    def stable(self, stable):
        if not isinstance(stable, bool):
            raise TypeError("stable must be a boolean")
        self._stable = stable
    
    @property
    def decay_modes(self):
        return self._decay_modes

    @decay_modes.setter
    def decay_modes(self, decay_modes):
        if not isinstance(decay_modes, list):
            raise TypeError("decay_modes must be a list")
        self._decay_modes = decay_modes

    

class Particle:
    def __init__(self, ParticleType, p, eta, phi, pt):
        self.ParticleType = ParticleType
        self.p = p
        self.eta = eta
        self.phi = phi
        self.pt = pt
    
    @property
    def ParticleType(self):
        return self._ParticleType

    @ParticleType.setter
    def ParticleType(self, ParticleType):
        if not isinstance(ParticleType, ParticleType):
            raise TypeError("ParticleType must be a ParticleType object")
        self._ParticleType = ParticleType
    
    @property
    def p(self):
        if not isinstance(self._p, np.array):
            raise TypeError("p must be an array")
        return self._p

    @p.setter
    def p(self, p):
        self._p = p
    
    @property
    def eta(self):
        if not isinstance(self._eta, float):
            raise TypeError("eta must be a float")
        return self._eta

    @eta.setter
    def eta(self, eta):
        self._eta = eta
    
    @property
    def phi(self):
        if not isinstance(self._phi, float):
            raise TypeError("phi must be a float")
        return self._phi

    @phi.setter
    def phi(self, phi):
        self._phi = phi
