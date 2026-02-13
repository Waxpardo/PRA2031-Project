import math
import numpy as np

class ParticleClass:
    def __init__(self, name, pdg, particle_class, mass, charge, stable, decay_modes):
        self.name = name
        self.pdg = pdg
        self.particle_class = particle_class
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
    def particle_class(self):
        return self._particle_class

    @particle_class.setter
    def particle_class(self, particle_class):
        if not isinstance(particle_class, str):
            raise TypeError("particle_class must be a string")
        self._particle_class = particle_class

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
        return self._charge

    @charge.setter
    def charge(self, charge):
        if not isinstance(charge, float):
            raise TypeError("charge must be a float")
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
    
    def __repr__(self):
        return f"ParticleType(name={self.name!r}, pdg={self.pdg})"

    def __eq__(self, other):
        if not isinstance(other, ParticleType):
            return NotImplemented
        return (self.name == other.name and self.pdg == other.pdg)

    def __str__(self):
        return f"{self.name} (PDG={self.pdg}, m={self.mass:.3f} GeV, q={self.charge:+.0f})"