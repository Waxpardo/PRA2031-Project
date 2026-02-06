


    

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
        if not isinstance(particle_type, ParticleClass):
            raise TypeError("particle_type must be a ParticleClass object")
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
