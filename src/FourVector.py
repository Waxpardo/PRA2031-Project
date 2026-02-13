import math
import numpy as np

class FourVector:
    """
    Represents a relativistic four-vector (E, px, py, pz). Provides accessors for
    energy/momentum components and derived kinematic quantities such as |p|, pT,
    invariant mass, pseudorapidity, and azimuthal angle. Includes a Lorentz boost
    method in natural units (c = 1).
    """

    metric = (1, -1, -1, -1)

    def __init__(self, e, px, py, pz):
        self.e = e # particle's energy energy
        self.px = px # x component of the momentum
        self.py = py # y component of the momentum
        self.pz = pz # z component of the momentum


    def __str__(self):
        return f"(E: {self.e:8.3f}, px: {self.px:8.3f}, py: {self.py:8.3f}, pz: {self.pz:8.3f})"

    def __repr__(self):
        return f"FourVector({self.e}, {self.px}, {self.py}, {self.pz})"

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
    def inv_mass2(self):
        """Invariant mass squared (E^2 - |p|^2)."""
        return self.e**2 - self.p2

    @property
    def inv_mass(self):
        """Invariant mass (non-negative)."""
        m2 = self.inv_mass2
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

    def __add__(self, other):
        if not isinstance(other, FourVector):
            return NotImplemented
        return FourVector(self.e + other.e, self.px + other.px, self.py + other.py, self.pz + other.pz)

    def __sub__(self, other):
        if not isinstance(other, FourVector):
            return NotImplemented
        return FourVector(self.e - other.e, self.px - other.px, self.py - other.py, self.pz - other.pz)

    def __mul__(self, a):
        if isinstance(a, (int, float)):
            return FourVector(self.e*a, self.px*a, self.py*a, self.pz*a)
        return NotImplemented

    def __rmul__(self, a):
        return self.__mul__(a)

    def __truediv__(self, a):
        if isinstance(a, (int, float)):
            if a == 0:
                raise ZeroDivisionError
            return FourVector(self.e/a, self.px/a, self.py/a, self.pz/a)
        return NotImplemented

    def dot(self, other):
        return self.e*other.e - self.px*other.px - self.py*other.py - self.pz*other.pz

    def __matmul__(self, other):
        if not isinstance(other, FourVector):
            return NotImplemented
        return self.dot(other)

    def __eq__(self, other):
        if not isinstance(other, FourVector):
            return NotImplemented
        return (self.e == other.e) & (self.px == other.px) & (self.py == other.py) & (self.pz == other.pz)
    
    def __lt__(self, other):
        if not isinstance(other, FourVector):
            return NotImplemented
        return self.pt < other.pt

    def __iter__(self):
        yield self.e; yield self.px; yield self.py; yield self.pz

    def __len__(self):
        return 4

    def __getitem__(self, i):
        return (self.e, self.px, self.py, self.pz)[i]

    def __neg__(self):
        return FourVector(-self.e, -self.px, -self.py, -self.pz)

    def __abs__(self):
        return self.inv_mass


