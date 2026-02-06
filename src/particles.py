
import numpy as np
import json
from pathlib import Path

def load_particle_types(json_path):
    """Return a dict: name -> ParticleType."""
    data = json.loads(Path(json_path).read_text())
    catalog = {}
    for item in data:
        ptype = ParticleType(
            name=item["name"],
            pdg=item["pdg"],
            particle_class=item["particle_class"],
            mass=item["mass"],
            charge=item["charge"],
            stable=item["stable"],
            decay_modes=item["decay_modes"],
        )
        catalog[ptype.name] = ptype
    return catalog

class ParticleType:
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
    
    def __repr__(self):
        return f"ParticleType(name={self.name!r}, pdg={self.pdg})"

    def __eq__(self, other):
        if not isinstance(other, ParticleType):
            return NotImplemented
        return (self.name == other.name and self.pdg == other.pdg)

    def __str__(self):
        return f"{self.name} (PDG={self.pdg}, m={self.mass:.3f} GeV, q={self.charge:+.0f})"


    

class Particle:
    def __init__(self, particle_type, p4, eta=0.0, phi=0.0, pt=0.0, mother=None, eventID=None):
        self.particle_type = particle_type
        self.p4 = p4
        self.eta = eta
        self.phi = phi
        self.pt = pt
        self.mother = mother
        self.eventID = eventID
    
    @property
    def particle_type(self):
        return self._particle_type

    @Pparticle_type.setter
    def particle_type(self, particle_type):
        if not isinstance(particle_type, ParticleType):
            raise TypeError("particle_type must be a ParticleType object")
        self._particle_type = particle_type
    
    @property
    def p4(self):
        if not isinstance(self._p4, FourVector):
            raise TypeError("p4 must be a FourVector object")
        return self._p4

    @p4.setter
    def p4(self, p4):
        self._p4 = p4
    
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

    @property
    def pt(self):
        if not isinstance(self._pt, float):
            raise TypeError("pt must be a float")
        return self._pt

    @pt.setter
    def pt(self, pt):
        self._pt = pt

    @property
    def mother(self):
        return self._mother

    @mother.setter
    def mother(self, mother):
        if not isinstance(mother, Particle):
            raise TypeError("mother must be a Particle object")
        self._mother = mother
    
    @property
    def eventID(self):
        return self._eventID

    @eventID.setter
    def eventID(self, eventID):
        if not isinstance(eventID, int):
            raise TypeError("eventID must be an integer")
        self._eventID = eventID
    
    def __str__(self):
        motherStr = self.mother if self.mother else "Initial Beam"
        return f"{self.eventID:03d} | {self.particle_type.pdg:>3} | {motherStr:<12} | {self.p4}"
