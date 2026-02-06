
import numpy as np
import json
from pathlib import Path

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


import math

class FourVector:
    """Mathematical object for Energy and Momentum [E, px, py, pz]."""

    def __init__(self, e_val, px_val, py_val, pz_val):
        self.e = e_val
        self.px = px_val
        self.py = py_val
        self.pz = pz_val

    # --- Core components ---
    @property
    def e(self):
        return self._e

    @e.setter
    def e(self, value):
        if not isinstance(value, (int, float)):
            raise TypeError("E must be a number")
        self._e = float(value)

    @property
    def px(self):
        return self._px

    @px.setter
    def px(self, value):
        if not isinstance(value, (int, float)):
            raise TypeError("px must be a number")
        self._px = float(value)

    @property
    def py(self):
        return self._py

    @py.setter
    def py(self, value):
        if not isinstance(value, (int, float)):
            raise TypeError("py must be a number")
        self._py = float(value)

    @property
    def pz(self):
        return self._pz

    @pz.setter
    def pz(self, value):
        if not isinstance(value, (int, float)):
            raise TypeError("pz must be a number")
        self._pz = float(value)

    # --- Derived quantities ---
    @property
    def p2(self):
        """Momentum magnitude squared."""
        return self.px**2 + self.py**2 + self.pz**2

    @property
    def p(self):
        """Momentum magnitude."""
        return math.sqrt(self.p2)

    @property
    def pt2(self):
        """Transverse momentum squared."""
        return self.px**2 + self.py**2

    @property
    def pt(self):
        """Transverse momentum."""
        return math.sqrt(self.pt2)

    @property
    def mass2(self):
        """Invariant mass squared (E^2 - |p|^2)."""
        return self.e**2 - self.p2

    @property
    def mass(self):
        """Invariant mass (non-negative)."""
        m2 = self.mass2
        return math.sqrt(m2) if m2 >= 0 else -math.sqrt(-m2)

    @property
    def eta(self):
        """Pseudorapidity."""
        p = self.p
        if p == abs(self.pz):
            return math.inf if self.pz >= 0 else -math.inf
        return 0.5 * math.log((p + self.pz) / (p - self.pz))

    @property
    def phi(self):
        """Azimuthal angle."""
        return math.atan2(self.py, self.px)

    # --- Operations ---
    def boost(self, beta_x=0.0, beta_y=0.0, beta_z=0.0):
        """
        Return a new FourVector boosted by velocity beta = (bx, by, bz).
        Uses units where c = 1.
        """
        beta2 = beta_x**2 + beta_y**2 + beta_z**2
        if beta2 >= 1.0:
            raise ValueError("Beta^2 must be < 1")

        gamma = 1.0 / math.sqrt(1.0 - beta2)
        bp = beta_x * self.px + beta_y * self.py + beta_z * self.pz
        gamma2 = (gamma - 1.0) / beta2 if beta2 > 0 else 0.0

        px_prime = self.px + gamma2 * bp * beta_x + gamma * beta_x * self.e
        py_prime = self.py + gamma2 * bp * beta_y + gamma * beta_y * self.e
        pz_prime = self.pz + gamma2 * bp * beta_z + gamma * beta_z * self.e
        e_prime = gamma * (self.e + bp)

        return FourVector(e_prime, px_prime, py_prime, pz_prime)

    def __repr__(self):
        return f"(E: {self.e:8.3f}, px: {self.px:8.3f}, py: {self.py:8.3f}, pz: {self.pz:8.3f})"

    

class Particle:
    def __init__(self, particle_type, p4, mother=None, eventID=None):
        self.particle_type = particle_type
        self.p4 = p4
        self.mother = mother
        self.eventID = eventID

    
    @property
    def particle_type(self):
        return self._particle_type

    @particle_type.setter
    def particle_type(self, particle_type):
        if not isinstance(particle_type, ParticleType):
            raise TypeError("particle_type must be a ParticleType object")
        self._particle_type = particle_type
        
    @property
    def pdg(self):
        return self.particle_type.pdg

    @property
    def mass(self):
        return self.particle_type.mass

    @property
    def charge(self):
        return self.particle_type.charge

    @property
    def particle_class(self):
        return self.particle_type.particle_class

    @property
    def stable(self):
        return self.particle_type.stable

    @property
    def decay_modes(self):
        return self.particle_type.decay_modes

    @property
    def p4(self):
        return self._p4

    @p4.setter
    def p4(self, p4):
        if not isinstance(p4, FourVector):
            raise TypeError("p4 must be a FourVector object")
        self._p4 = p4

    @property
    def eta(self):
        return self.p4.eta

    @property
    def phi(self):
        return self.p4.phi

    @property
    def pt(self):
        return self.p4.pt

    @property
    def mother(self):
        return self._mother

    @mother.setter
    def mother(self, mother):
        if mother is not None and not isinstance(mother, Particle):
            raise TypeError("mother must be a Particle object or None")
        self._mother = mother

    @property
    def eventID(self):
        return self._eventID

    @eventID.setter
    def eventID(self, eventID):
        if eventID is not None and not isinstance(eventID, int):
            raise TypeError("eventID must be an integer or None")
        self._eventID = eventID

    def __str__(self):
        motherStr = self.mother if self.mother else "Initial Beam"
        return f"{self.eventID:03d} | {self.particle_type.pdg:>3} | {motherStr:<12} | {self.p4}"
