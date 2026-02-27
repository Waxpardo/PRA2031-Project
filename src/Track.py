import math
from Particle import Particle
from FourVector import FourVector


class Track:
    """
    Represents a reconstructed path of a particle.
    In complex simulations, a track might consist of several segments
    if a particle decays or interacts while traveling.
    """

    def __init__(self, particles=None):
        # We use internalParticles to store the list without the '_' prefix
        self.internalParticles = particles if particles else []

    @property
    def Particles(self):
        return self.internalParticles

    @Particles.setter
    def Particles(self, particles):
        # Safety check: ensures we are only tracking actual Particle objects
        if not all(isinstance(p, Particle) for p in particles):
            raise TypeError("All elements must be Particle objects")
        self.internalParticles = particles

    def AddParticle(self, particle):
        """Adds a new segment or particle to this specific track."""
        if not isinstance(particle, Particle):
            raise TypeError("particle must be a Particle object")
        self.internalParticles.append(particle)

    @property
    def EventID(self):
        """Links the track back to its specific collision event."""
        return self.internalParticles[0].eventID if self.internalParticles else None

    @property
    def TotalP4(self):
        """
        Calculates the combined 'Four-Momentum' of the track.
        This represents the total energy and directional flow of the path.
        """
        if not self.internalParticles:
            return None
        total = FourVector(0, 0, 0, 0)
        for p in self.internalParticles:
            total = FourVector(
                total.e + p.p4.e,
                total.px + p.p4.px,
                total.py + p.p4.py,
                total.pz + p.p4.pz,
            )
        return total

    @property
    def AvgPt(self):
        """
        Calculates the average Transverse Momentum (pT).
        pT is the momentum perpendicular to the beam—high pT usually
        indicates a very 'interesting' or high-energy collision.
        """
        return sum(p.pt for p in self.internalParticles) / len(
            self.internalParticles) if self.internalParticles else 0.0

    @property
    def Length(self):
        """
        Calculates the physical length of the track in momentum-space.
        In this simulator, it represents the 'distance' covered by the particle's vector.
        """
        if len(self.internalParticles) < 2:
            return 0.0
        trackLength = 0.0
        for i in range(1, len(self.internalParticles)):
            # Distance formula in 3D: sqrt(dx^2 + dy^2 + dz^2)
            dx = self.internalParticles[i].p4.px - self.internalParticles[i - 1].p4.px
            dy = self.internalParticles[i].p4.py - self.internalParticles[i - 1].p4.py
            dz = self.internalParticles[i].p4.pz - self.internalParticles[i - 1].p4.pz
            trackLength += math.sqrt(dx ** 2 + dy ** 2 + dz ** 2)
        return trackLength

    def __str__(self):
        return f"Track(eventID={self.EventID}, particles={len(self.internalParticles)}, total_p4={self.TotalP4})"


class TrackFollowing:
    """
    The algorithm that 'connects the dots.'
    It looks at all particles in an event and groups them into logical
    tracks based on their 'Mother' relationship.
    """

    def __init__(self):
        self.tracks = []

    def Solve(self, event):
        """
        Organizes a list of particles into a list of Track objects.
        """
        self.tracks = []
        particleToTrack = {}

        for particle in event:
            # If a particle knows its mother, it belongs to the same path as its mother.
            if particle.mother and isinstance(particle.mother, Particle) and particle.mother in particleToTrack:
                track = particleToTrack[particle.mother]
            else:
                # Otherwise, it is a primary particle that starts a brand new track.
                track = Track()
                self.tracks.append(track)

            track.AddParticle(particle)
            particleToTrack[particle] = track

        return self.tracks


class TrackVisualizer:
    """
    Generates 3D graphics and animations to show the particles flying
    out from the collision point.
    """

    def __init__(self, tracks):
        self.tracks = tracks

    def Plot3d(self, title="Particle Track Tracing", show=True, savePath=None):
        """
        Creates a static 3D vector map of the event.
        Since we track momentum (P), the 'length' of the line on the
        graph represents how much momentum the particle has.
        """
        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d import Axes3D

        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')

        for i, track in enumerate(self.tracks):
            p = track.Particles[0] if track.Particles else None
            if not p:
                continue

            # In a collider, 'Beams' come from the outside toward (0,0,0).
            # 'Collision' products fly from (0,0,0) toward the outside.
            isBeam = p.mother is None

            if isBeam:
                # Draw the incoming beam particle
                currPos = [-p.p4.px, -p.p4.py, -p.p4.pz]
            else:
                # Draw the outgoing scattering result
                currPos = [0, 0, 0]

            for p in track.Particles:
                nextPos = [
                    currPos[0] + p.p4.px,
                    currPos[1] + p.p4.py,
                    currPos[2] + p.p4.pz
                ]

                label = f"PDG: {p.pdg} ({p.particleType.name})" if len(self.tracks) < 10 else None
                ax.plot([currPos[0], nextPos[0]],
                        [currPos[1], nextPos[1]],
                        [currPos[2], nextPos[2]],
                        label=label, linewidth=2)

                # Label the particle at its final position
                if len(self.tracks) < 20:
                    ax.text(nextPos[0], nextPos[1], nextPos[2], f"{p.particleType.name}", fontsize=8)

                currPos = nextPos

        ax.set_xlabel('px (GeV)')
        ax.set_ylabel('py (GeV)')
        ax.set_zlabel('pz (GeV)')
        ax.set_title(title)

        if len(self.tracks) < 10:
            ax.legend()

        if savePath:
            plt.savefig(savePath)
            print(f"Static plot saved to: {savePath}")

        if show:
            plt.show()
        return fig, ax

    def AnimateTracks(self, title="Animated Particle Track Tracing", interval=50, savePath=None):
        """
        Creates an animation where you can see the beams approach
        the center, collide, and explode into new particles.
        """
        import matplotlib.pyplot as plt
        from matplotlib.animation import FuncAnimation
        from mpl_toolkits.mplot3d import Axes3D

        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')

        # Logic to scale the 'box' so all particle tracks fit on screen
        maxVal = 0
        for track in self.tracks:
            p = track.Particles[0] if track.Particles else None
            if not p: continue

            isBeam = p.mother is None
            if isBeam:
                maxVal = max(maxVal, abs(p.p4.px), abs(p.p4.py), abs(p.p4.pz))
            else:
                curr = [0, 0, 0]
                for pPart in track.Particles:
                    curr[0] += pPart.p4.px
                    curr[1] += pPart.p4.py
                    curr[2] += pPart.p4.pz
                    maxVal = max(maxVal, abs(curr[0]), abs(curr[1]), abs(curr[2]))

        ax.set_xlim(-maxVal, maxVal)
        ax.set_ylim(-maxVal, maxVal)
        ax.set_zlim(-maxVal, maxVal)
        ax.set_xlabel('px (GeV)')
        ax.set_ylabel('py (GeV)')
        ax.set_zlabel('pz (GeV)')
        ax.set_title(title)

        lines = [ax.plot([], [], [], linewidth=2)[0] for _ in self.tracks]
        texts = [ax.text(0, 0, 0, "", fontsize=8) for _ in self.tracks]

        def Init():
            for line in lines:
                line.set_data([], [])
                line.set_3d_properties([])
            for text in texts:
                text.set_text("")
            return lines + texts

        def Update(frame):
            # Frame 0-50: Particles flying IN. Frame 51-100: Particles flying OUT.
            splitFrame = 50

            for i, track in enumerate(self.tracks):
                pFirst = track.Particles[0] if track.Particles else None
                if not pFirst: continue

                isBeam = pFirst.mother is None
                xData, yData, zData = [], [], []

                if isBeam:
                    # Incoming beams move toward 0,0,0
                    if frame <= splitFrame:
                        fraction = frame / float(splitFrame)
                    else:
                        fraction = 1.0

                    startPos = [-pFirst.p4.px, -pFirst.p4.py, -pFirst.p4.pz]
                    endPos = [
                        startPos[0] + pFirst.p4.px * fraction,
                        startPos[1] + pFirst.p4.py * fraction,
                        startPos[2] + pFirst.p4.pz * fraction
                    ]
                    xData, yData, zData = [startPos[0], endPos[0]], [startPos[1], endPos[1]], [startPos[2], endPos[2]]

                    if frame > 0:
                        texts[i].set_position((endPos[0], endPos[1]))
                        texts[i].set_3d_properties(endPos[2])
                        texts[i].set_text(pFirst.particleType.name)
                else:
                    # Outgoing particles move away from 0,0,0
                    if frame < splitFrame:
                        fraction = 0.0
                    else:
                        fraction = (frame - splitFrame) / float(100 - splitFrame)

                    currPos = [0, 0, 0]
                    xData.append(currPos[0])
                    yData.append(currPos[1])
                    zData.append(currPos[2])

                    for p in track.Particles:
                        nextPos = [
                            currPos[0] + p.p4.px * fraction,
                            currPos[1] + p.p4.py * fraction,
                            currPos[2] + p.p4.pz * fraction
                        ]
                        xData.append(nextPos[0])
                        yData.append(nextPos[1])
                        zData.append(nextPos[2])

                        if frame >= splitFrame:
                            texts[i].set_position((nextPos[0], nextPos[1]))
                            texts[i].set_3d_properties(nextPos[2])
                            texts[i].set_text(p.particleType.name)
                        else:
                            texts[i].set_text("")

                lines[i].set_data(xData, yData)
                lines[i].set_3d_properties(zData)
            return lines + texts

        ani = FuncAnimation(fig, Update, frames=range(0, 101, 2), init_func=Init,
                            blit=False, interval=interval, repeat=True)

        if savePath:
            savePathStr = str(savePath)
            print(f"Saving animation to: {savePathStr}...")
            if savePathStr.endswith('.gif'):
                ani.save(savePathStr, writer='pillow')
            else:
                ani.save(savePathStr)

        plt.show()
        return ani