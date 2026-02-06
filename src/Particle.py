import math
from FourVector import FourVector
from ParticleClass import ParticleClass


class Particle:
    def __init__(self, particleType, p4, mother=None, eventID=None):
        # Using nameName convention for internal attributes
        self.particleType = particleType
        self.p4 = p4
        self.mother = mother
        self.eventID = eventID

    @property
    def particleType(self):
        return self._particleType

    @particleType.setter
    def particleType(self, value):
        if not isinstance(value, ParticleClass):
            raise TypeError("particleType must be a ParticleClass object")
        self._particleType = value

    @property
    def p4(self):
        return self._p4

    @p4.setter
    def p4(self, value):
        if not isinstance(value, FourVector):
            raise TypeError("p4 must be a FourVector object")
        self._p4 = value

    @property
    def mother(self):
        return self._mother

    @mother.setter
    def mother(self, value):
        # Updated to allow strings so "Collision" doesn't crash the code
        if value is not None and not isinstance(value, (Particle, str)):
            raise TypeError("mother must be a Particle object, a string, or None")
        self._mother = value

    @property
    def eventID(self):
        return self._eventID

    @eventID.setter
    def eventID(self, value):
        if value is not None and not isinstance(value, int):
            raise TypeError("eventID must be an integer or None")
        self._eventID = value

    # Helper properties to reach into ParticleClass
    @property
    def pdg(self):
        return self.particleType.pdg

    @property
    def mass(self):
        return self.particleType.mass

    @property
    def charge(self):
        return self.particleType.charge

    def __str__(self):
        # If mother is a Particle object, show its name, otherwise show the string/default
        motherDisplayName = self.mother.particleType.name if isinstance(self.mother, Particle) else str(self.mother)
        motherStr = motherDisplayName if self.mother else "Initial Beam"

        return f"{self.eventID:03d} | {self.pdg:>3} | {motherStr:<12} | {self.p4}"