import math
from FourVector.py import FourVector
from ParticleClass.py import ParticleClass

class Particle:
    """
    Represents a particle in an event. A Particle has a ParticleClass (shared properties
    like mass, charge, PDG code, and decay channels) and a FourVector that stores its
    energy and momentum components (px, py, pz), as well as derived quantities such as
    pT, pseudorapidity, and azimuthal angle. For bookkeeping, each particle can store
    an eventID and an optional mother reference to link decay chains.
    """

    def __init__(self, particle_type, p4, mother=None, eventID=None):
        self.particle_type = particle_type
        self.p4 = p4
        self.mother = mother
        self.eventID = eventID

    # particle_type
    @property
    def particle_type(self):
        return self._particle_type

    @particle_type.setter
    def particle_type(self, particle_type):
        if not isinstance(particle_type, ParticleClass):
            raise TypeError("particle_type must be a ParticleClass object")
        self._particle_type = particle_type

    # Pardicle Data Group (pdg)
    @property
    def pdg(self):
        return self.particle_type.pdg

    # Mass
    @property
    def mass(self):
        return self.particle_type.mass


    # Charge
    @property
    def charge(self):
        return self.particle_type.charge


    # Particle class
    @property
    def particle_class(self):
        return self.particle_type.particle_class


    # Stable
    @property
    def stable(self):
        return self.particle_type.stable


    # Decay modes
    @property
    def decay_modes(self):
        return self.particle_type.decay_modes


    # Four momentum (p4)
    @property
    def p4(self):
        return self._p4

    @p4.setter
    def p4(self, p4):
        if not isinstance(p4, FourVector):
            raise TypeError("p4 must be a FourVector object")
        self._p4 = p4

    @property
    def e(self): return self.p4.e
    @property
    def px(self): return self.p4.px
    @property
    def py(self): return self.p4.py
    @property
    def pz(self): return self.p4.pz
    @property
    def inv_mass(self): return self.p4.inv_mass



    # Pseudorapidity (eta)
    @property
    def eta(self):
        return self.p4.eta

    # azimuthal angle (phi)
    @property
    def phi(self):
        return self.p4.phi

    # Trnasverse momentum (pt)
    @property
    def pt(self):
        return self.p4.pt

    # mother
    @property
    def mother(self):
        return self._mother

    @mother.setter
    def mother(self, mother):
        if mother is not None and not isinstance(mother, Particle):
            raise TypeError("mother must be a Particle object or None")
        self._mother = mother

    # eventID
    @property
    def eventID(self):
        return self._eventID

    @eventID.setter
    def eventID(self, eventID):
        if eventID is not None and not isinstance(eventID, int):
            raise TypeError("eventID must be an integer or None")
        self._eventID = eventID

    # String representation
    def __str__(self):
        eid = "---" if self.eventID is None else f"{self.eventID:03d}"
        mother_str = "Initial" if self.mother is None else f"PDG {self.mother.pdg}"
        return f"{eid} | {self.pdg:>6} | {mother_str:<10} | {self.p4}"

    
    def __repr__(self):
    return f"Particle(pdg={self.pdg}, p4={self.p4!r}, eventID={self.eventID})"

