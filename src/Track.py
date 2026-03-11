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

    def _Theme(self):
        return {
            "figure_bg": "#05070a",
            "pane": (0.05, 0.07, 0.10, 1.0),
            "text": "#d9e2f2",
            "subtext": "#9fb3c8",
            "grid": (1.0, 1.0, 1.0, 0.08),
            "pane_edge": (1.0, 1.0, 1.0, 0.12),
            "beam": (0.72, 0.78, 0.88, 1.0),
        }

    def _TrackCoordinates(self, track, fraction=1.0):
        """Build the 3D polyline for a track at a given animation fraction."""
        pFirst = track.Particles[0] if track.Particles else None
        if not pFirst:
            return [], [], [], None, False

        isBeam = pFirst.mother is None

        if isBeam:
            startPos = [-pFirst.p4.px, -pFirst.p4.py, -pFirst.p4.pz]
            endPos = [
                startPos[0] + pFirst.p4.px * fraction,
                startPos[1] + pFirst.p4.py * fraction,
                startPos[2] + pFirst.p4.pz * fraction,
            ]
            return [startPos[0], endPos[0]], [startPos[1], endPos[1]], [startPos[2], endPos[2]], endPos, True

        currPos = [0.0, 0.0, 0.0]
        xData, yData, zData = [currPos[0]], [currPos[1]], [currPos[2]]

        for particle in track.Particles:
            nextPos = [
                currPos[0] + particle.p4.px * fraction,
                currPos[1] + particle.p4.py * fraction,
                currPos[2] + particle.p4.pz * fraction,
            ]
            xData.append(nextPos[0])
            yData.append(nextPos[1])
            zData.append(nextPos[2])
            currPos = nextPos

        return xData, yData, zData, currPos, False

    def _TracksGroupedByEvent(self):
        """Split combined tracks into event-sized groups using their event IDs."""
        grouped = {}
        for track in self.tracks:
            eventID = track.EventID
            if eventID not in grouped:
                grouped[eventID] = []
            grouped[eventID].append(track)

        sortKey = lambda eventID: -1 if eventID is None else eventID
        return [grouped[eventID] for eventID in sorted(grouped, key=sortKey)]

    def _GetEventColors(self, trackGroups=None):
        """Assign stable event colors so all renderers share the same palette."""
        import matplotlib.pyplot as plt

        if trackGroups is None:
            trackGroups = self._TracksGroupedByEvent()

        eventIDs = [group[0].EventID for group in trackGroups if group]
        if not eventIDs:
            return {}

        if len(eventIDs) == 1:
            return {eventIDs[0]: (0.98, 0.62, 0.20, 1.0)}

        colors = {}
        for index, eventID in enumerate(eventIDs):
            colors[eventID] = plt.cm.plasma(0.15 + 0.75 * (index / (len(eventIDs) - 1)))
        return colors

    def _TrackColor(self, track, eventColors):
        theme = self._Theme()
        firstParticle = track.Particles[0] if track.Particles else None
        if not firstParticle:
            return theme["beam"]
        if firstParticle.mother is None:
            return theme["beam"]
        return eventColors.get(track.EventID, (0.98, 0.62, 0.20, 1.0))

    def _GetMaxExtent(self, trackGroups=None):
        """Estimate a common axis scale that fits all provided tracks."""
        if trackGroups is None:
            flatTracks = self.tracks
        else:
            flatTracks = [track for group in trackGroups for track in group]

        maxVal = 0.0
        for track in flatTracks:
            xData, yData, zData, _, _ = self._TrackCoordinates(track, fraction=1.0)
            for value in xData + yData + zData:
                maxVal = max(maxVal, abs(value))

        return maxVal if maxVal > 0 else 1.0

    def _ApplyColliderTheme(self, fig, ax, title, maxVal):
        """Apply a consistent dark collider theme to plots and animations."""
        theme = self._Theme()

        fig.patch.set_facecolor(theme["figure_bg"])
        ax.set_facecolor(theme["figure_bg"])

        for axis in (ax.xaxis, ax.yaxis, ax.zaxis):
            axis.pane.set_facecolor(theme["pane"])
            axis.pane.set_edgecolor(theme["pane_edge"])
            axis._axinfo["grid"]["color"] = theme["grid"]
            axis._axinfo["axisline"]["color"] = theme["subtext"]

        ax.set_xlim(-maxVal, maxVal)
        ax.set_ylim(-maxVal, maxVal)
        ax.set_zlim(-maxVal, maxVal)
        ax.set_xlabel('px (GeV)', color=theme["text"])
        ax.set_ylabel('py (GeV)', color=theme["text"])
        ax.set_zlabel('pz (GeV)', color=theme["text"])
        ax.set_title(title, color=theme["text"], pad=14)
        ax.tick_params(colors=theme["text"])
        return theme

    def Plot3d(self, title="Particle Track Tracing", show=True, savePath=None):
        """
        Creates a static 3D vector map of the event.
        Since we track momentum (P), the 'length' of the line on the
        graph represents how much momentum the particle has.
        """
        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d import Axes3D

        trackGroups = self._TracksGroupedByEvent()
        eventColors = self._GetEventColors(trackGroups)

        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')
        theme = self._ApplyColliderTheme(fig, ax, title, self._GetMaxExtent(trackGroups) * 1.1)

        for track in self.tracks:
            p = track.Particles[0] if track.Particles else None
            if not p:
                continue

            isBeam = p.mother is None
            xData, yData, zData, finalPos, _ = self._TrackCoordinates(track, fraction=1.0)
            lineColor = self._TrackColor(track, eventColors)
            lineWidth = 1.6 if isBeam else 2.5
            label = f"PDG: {p.pdg} ({p.particleType.name})" if len(self.tracks) < 10 else None

            ax.plot(xData, yData, zData, label=label, linewidth=lineWidth,
                    color=lineColor, alpha=0.95, solid_capstyle='round')

            if len(self.tracks) < 20 and finalPos is not None:
                ax.text(finalPos[0], finalPos[1], finalPos[2], f"{p.particleType.name}",
                        fontsize=8, color=theme["text"])

        if len(self.tracks) < 10:
            legend = ax.legend(facecolor=theme["figure_bg"], edgecolor=theme["pane_edge"])
            if legend is not None:
                for text in legend.get_texts():
                    text.set_color(theme["text"])

        if savePath:
            plt.savefig(savePath, facecolor=fig.get_facecolor(), dpi=200, bbox_inches='tight')
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

        trackGroups = self._TracksGroupedByEvent()
        eventColors = self._GetEventColors(trackGroups)

        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')
        theme = self._ApplyColliderTheme(fig, ax, title, self._GetMaxExtent(trackGroups) * 1.1)

        lines = []
        texts = []
        for track in self.tracks:
            p = track.Particles[0] if track.Particles else None
            if not p:
                continue
            isBeam = p.mother is None
            lineColor = self._TrackColor(track, eventColors)
            lineWidth = 1.6 if isBeam else 2.5
            lines.append(ax.plot([], [], [], linewidth=lineWidth, color=lineColor,
                                 alpha=0.98, solid_capstyle='round')[0])
            texts.append(ax.text(0, 0, 0, "", fontsize=8, color=theme["text"]))

        activeTracks = [track for track in self.tracks if track.Particles]

        def Init():
            for line in lines:
                line.set_data([], [])
                line.set_3d_properties([])
            for text in texts:
                text.set_text("")
            return lines + texts

        def Update(frame):
            splitFrame = 50

            for i, track in enumerate(activeTracks):
                pFirst = track.Particles[0]
                isBeam = pFirst.mother is None

                if isBeam:
                    fraction = frame / float(splitFrame) if frame <= splitFrame else 1.0
                    xData, yData, zData, finalPos, _ = self._TrackCoordinates(track, fraction)
                    if frame > 0 and finalPos is not None:
                        texts[i].set_position((finalPos[0], finalPos[1]))
                        texts[i].set_3d_properties(finalPos[2])
                        texts[i].set_text(pFirst.particleType.name)
                else:
                    if frame < splitFrame:
                        fraction = 0.0
                        texts[i].set_text("")
                    else:
                        fraction = (frame - splitFrame) / float(100 - splitFrame)
                    xData, yData, zData, finalPos, _ = self._TrackCoordinates(track, fraction)
                    if frame >= splitFrame and finalPos is not None:
                        texts[i].set_position((finalPos[0], finalPos[1]))
                        texts[i].set_3d_properties(finalPos[2])
                        texts[i].set_text(track.Particles[-1].particleType.name)

                lines[i].set_data(xData, yData)
                lines[i].set_3d_properties(zData)
            return lines + texts

        ani = FuncAnimation(fig, Update, frames=range(0, 101, 2), init_func=Init,
                            blit=False, interval=interval, repeat=True)

        if savePath:
            savePathStr = str(savePath)
            print(f"Saving animation to: {savePathStr}...")
            saveKwargs = {"facecolor": fig.get_facecolor()}
            if savePathStr.endswith('.gif'):
                ani.save(savePathStr, writer='pillow', savefig_kwargs=saveKwargs)
            else:
                ani.save(savePathStr, savefig_kwargs=saveKwargs)

        plt.show()
        return ani

    def AnimateCollisionSequence(self, title="Sequential Collider Collision Stack", interval=70,
                                 framesPerEvent=30, holdFrames=6, savePath=None, show=True):
        """
        Animate several events one after another while keeping completed tracks on screen.
        This creates a collider-style view where each collision accumulates in the
        same interaction region.
        """
        import matplotlib.pyplot as plt
        from matplotlib.animation import FuncAnimation
        from mpl_toolkits.mplot3d import Axes3D

        trackGroups = self._TracksGroupedByEvent()
        if not trackGroups:
            raise ValueError("No tracks available for sequential collision animation.")

        fig = plt.figure(figsize=(11, 8))
        ax = fig.add_subplot(111, projection='3d')
        theme = self._ApplyColliderTheme(fig, ax, title, self._GetMaxExtent(trackGroups) * 1.1)
        eventColors = self._GetEventColors(trackGroups)

        lineGroups = []
        for eventTracks in trackGroups:
            artists = []
            for track in eventTracks:
                firstParticle = track.Particles[0] if track.Particles else None
                if not firstParticle:
                    continue
                isBeam = firstParticle.mother is None
                lineColor = self._TrackColor(track, eventColors)
                lineWidth = 1.6 if isBeam else 2.5
                line = ax.plot([], [], [], color=lineColor, linewidth=lineWidth, alpha=0.0,
                               solid_capstyle='round')[0]
                artists.append((line, isBeam, track))
            lineGroups.append(artists)

        headerText = ax.text2D(0.03, 0.95, "", transform=ax.transAxes,
                               color=theme["text"], fontsize=12, fontweight='bold')
        subText = ax.text2D(0.03, 0.91,
                            "Completed collisions remain visible to build a collider-style event stack.",
                            transform=ax.transAxes, color=theme["subtext"], fontsize=9)

        incomingFrames = max(1, int(framesPerEvent * 0.45))
        outgoingFrames = max(1, framesPerEvent - incomingFrames)
        totalFrames = len(trackGroups) * (framesPerEvent + holdFrames) + holdFrames

        def Init():
            for artists in lineGroups:
                for line, _, _ in artists:
                    line.set_data([], [])
                    line.set_3d_properties([])
                    line.set_alpha(0.0)
            headerText.set_text("")
            return [line for artists in lineGroups for line, _, _ in artists] + [headerText, subText]

        def Update(frame):
            activeEvent = None
            completedEvents = 0

            for eventIndex, artists in enumerate(lineGroups):
                eventStart = eventIndex * (framesPerEvent + holdFrames)
                localFrame = frame - eventStart

                if localFrame < 0:
                    phase = "future"
                elif localFrame < framesPerEvent:
                    phase = "active"
                    activeEvent = eventIndex
                else:
                    phase = "past"
                    completedEvents += 1

                for line, isBeam, track in artists:
                    if phase == "future":
                        xData, yData, zData = [], [], []
                        alpha = 0.0
                    else:
                        if phase == "past":
                            fraction = 1.0
                            alpha = 0.20 if isBeam else 0.58
                        else:
                            if isBeam:
                                fraction = min(localFrame / float(incomingFrames), 1.0)
                                alpha = 0.42
                            else:
                                if localFrame < incomingFrames:
                                    fraction = 0.0
                                else:
                                    fraction = min((localFrame - incomingFrames) / float(outgoingFrames), 1.0)
                                alpha = 0.96

                        xData, yData, zData, _, _ = self._TrackCoordinates(track, fraction)

                    line.set_data(xData, yData)
                    line.set_3d_properties(zData)
                    line.set_alpha(alpha)

            if activeEvent is not None:
                eventID = trackGroups[activeEvent][0].EventID
                headerText.set_text(f"Collision {activeEvent + 1}/{len(trackGroups)}  |  Event {eventID}")
            elif completedEvents >= len(trackGroups):
                headerText.set_text(f"Accumulated collisions: {len(trackGroups)}")
            else:
                nextEvent = min(completedEvents, len(trackGroups) - 1)
                eventID = trackGroups[nextEvent][0].EventID
                headerText.set_text(f"Preparing collision {nextEvent + 1}/{len(trackGroups)}  |  Event {eventID}")

            return [line for artists in lineGroups for line, _, _ in artists] + [headerText, subText]

        ani = FuncAnimation(fig, Update, frames=range(totalFrames), init_func=Init,
                            blit=False, interval=interval, repeat=True)

        if savePath:
            savePathStr = str(savePath)
            print(f"Saving sequential collision animation to: {savePathStr}...")
            saveKwargs = {"facecolor": fig.get_facecolor()}
            if savePathStr.endswith('.gif'):
                ani.save(savePathStr, writer='pillow', savefig_kwargs=saveKwargs)
            else:
                ani.save(savePathStr, savefig_kwargs=saveKwargs)

        if show:
            plt.show()
        return ani