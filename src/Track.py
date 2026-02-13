import math
from Particle import Particle
from FourVector import FourVector

class Track:
    """
    Represents a reconstructed particle track (path) with multiple particles.
    """
    def __init__(self, particles=None):
        self.particles = particles if particles else []

    @property
    def particles(self):
        return self._particles

    @particles.setter
    def particles(self, particles):
        if not all(isinstance(p, Particle) for p in particles):
            raise TypeError("All elements must be Particle objects")
        self._particles = particles

    def add_particle(self, particle):
        if not isinstance(particle, Particle):
            raise TypeError("particle must be a Particle object")
        self._particles.append(particle)

    @property
    def eventID(self):
        return self._particles[0].eventID if self._particles else None

    @property
    def total_p4(self):
        if not self._particles:
            return None
        total = FourVector(0, 0, 0, 0)
        for p in self._particles:
            total = FourVector(
                total.e + p.p4.e,
                total.px + p.p4.px,
                total.py + p.p4.py,
                total.pz + p.p4.pz,
            )
        return total

    @property
    def avg_pt(self):
        return sum(p.pt for p in self._particles) / len(self._particles) if self._particles else 0.0

    @property
    def length(self):
        if len(self._particles) < 2:
            return 0.0
        length = 0.0
        for i in range(1, len(self._particles)):
            dx = self._particles[i].p4.px - self._particles[i - 1].p4.px
            dy = self._particles[i].p4.py - self._particles[i - 1].p4.py
            dz = self._particles[i].p4.pz - self._particles[i - 1].p4.pz
            length += math.sqrt(dx**2 + dy**2 + dz**2)
        return length

    def __str__(self):
        return f"Track(eventID={self.eventID}, particles={len(self._particles)}, total_p4={self.total_p4})"

# -----------------------------
# Track following algorithm
# -----------------------------
class TrackFollowing:
    """
    Reconstructs tracks from an event (list of Particle objects).
    Uses a simple algorithm:
    - Each particle starts a new track unless it has a mother particle
    - Particles with a mother are added to the same track as their mother
    """

    def __init__(self):
        self.tracks = []

    def solve(self, event):
        """
        Reconstruct tracks for a given event.
        event: list of Particle objects
        returns: list of Track objects
        """
        self.tracks = []
        particle_to_track = {}

        # Step 1: loop over all particles in the event
        for particle in event:
            # If particle has a mother, inherit mother's track
            if particle.mother and particle.mother in particle_to_track:
                track = particle_to_track[particle.mother]
            else:
                # Start a new track
                track = Track()
                self.tracks.append(track)

            # Add particle to track
            track.add_particle(particle)
            particle_to_track[particle] = track

        return self.tracks