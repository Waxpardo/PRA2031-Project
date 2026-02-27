# Define a class to represent particle properties in physics
class ParticleClass:
    def __init__(self, name, pdg, particle_class, mass, charge, stable, decay_modes):
        self.name = name
        self.pdg = pdg
        self.particle_class = particle_class
        self.mass = mass
        self.charge = charge
        self.stable = stable
        self.decay_modes = decay_modes

    # -------------------
    # Property: name
    # -------------------
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        if not isinstance(name, str):
            raise TypeError("name must be a string")
        self._name = name

    # -------------------
    # Property: pdg
    # -------------------
    @property
    def pdg(self):
        return self._pdg

    @pdg.setter
    def pdg(self, pdg):
        if not isinstance(pdg, int):
            raise TypeError("pdg must be an integer")
        self._pdg = pdg

    # -------------------
    # Property: particle_class
    # -------------------
    @property
    def particle_class(self):
        return self._particle_class

    @particle_class.setter
    def particle_class(self, particle_class):
        if not isinstance(particle_class, str):
            raise TypeError("particle_class must be a string")
        self._particle_class = particle_class

    # -------------------
    # Property: mass
    # -------------------
    @property
    def mass(self):
        return self._mass

    @mass.setter
    def mass(self, mass):
        if not isinstance(mass, (int, float)):
            raise TypeError("mass must be a number")
        if mass < 0:
            raise ValueError("mass must be non-negative")
        self._mass = float(mass)

    # -------------------
    # Property: charge
    # -------------------
    @property
    def charge(self):
        return self._charge

    @charge.setter
    def charge(self, charge):
        if not isinstance(charge, (int, float)):
            raise TypeError("charge must be a number")
        self._charge = float(charge)

    # -------------------
    # Property: stable
    # -------------------
    @property
    def stable(self):
        return self._stable

    @stable.setter
    def stable(self, stable):
        if not isinstance(stable, bool):
            raise TypeError("stable must be a boolean")
        self._stable = stable

    # -------------------
    # Property: decay_modes
    # -------------------
    @property
    def decay_modes(self):
        return self._decay_modes

    @decay_modes.setter
    def decay_modes(self, decay_modes):
        if not isinstance(decay_modes, list):
            raise TypeError("decay_modes must be a list of dictionaries")

        total_br = 0.0
        normalized_modes = []

        for mode in decay_modes:
            if not isinstance(mode, dict):
                raise TypeError("Each decay mode must be a dictionary")

            if "br" not in mode:
                raise ValueError("Each decay mode must contain 'br'")

            if "products" in mode:
                products = mode["products"]
            elif "daughters" in mode:
                products = mode["daughters"]
            else:
                raise ValueError("Each decay mode must contain 'products' or 'daughters'")

            br = mode["br"]
            if not isinstance(br, (int, float)):
                raise TypeError("Branching ratio must be a number")
            if br < 0 or br > 1:
                raise ValueError("Branching ratio must be between 0 and 1")

            if not isinstance(products, list):
                raise TypeError("'products' must be a list of PDG IDs or particle names")

            normalized_products = []
            for product in products:
                if not isinstance(product, (int, str)):
                    raise TypeError("Decay products must be integers (PDG) or strings (particle names)")
                if isinstance(product, str) and not product:
                    raise ValueError("Decay product names must be non-empty strings")
                normalized_products.append(product)

            total_br += float(br)
            normalized_modes.append({"br": float(br), "products": normalized_products})

        if total_br > 1.000001:
            raise ValueError(f"Total branching ratio exceeds 1: {total_br}")

        self._decay_modes = normalized_modes

    def __repr__(self):
        return f"ParticleClass(name={self.name!r}, pdg={self.pdg})"

    def __eq__(self, other):
        if not isinstance(other, ParticleClass):
            return NotImplemented
        return self.pdg == other.pdg

    def __str__(self):
        return f"{self.name} (PDG={self.pdg}, m={self.mass:.3f} GeV, q={self.charge:+g})"

    def __hash__(self):
        return hash(self.pdg)
