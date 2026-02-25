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
            if particle.mother and isinstance(particle.mother, Particle) and particle.mother in particle_to_track:
                track = particle_to_track[particle.mother]
            else:
                # Start a new track
                track = Track()
                self.tracks.append(track)

            # Add particle to track
            track.add_particle(particle)
            particle_to_track[particle] = track

        return self.tracks

class TrackVisualizer:
    """
    Provides visualization for particle tracks.
    """
    def __init__(self, tracks):
        self.tracks = tracks

    def plot_3d(self, title="Particle Track Tracing", show=True, save_path=None):
        """
        Plots the tracks in a 3D plot.
        Note: Since we only have momentum and not positions, 
        we simulate the track as a vector from the origin (0,0,0).
        """
        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d import Axes3D

        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')

        for i, track in enumerate(self.tracks):
            # Starting point:
            # For final particles (mother is not None), start from 0,0,0 and go to p
            # For initial beams (mother is None), start from -p and go to 0,0,0
            
            p = track.particles[0] if track.particles else None
            if not p:
                continue

            is_beam = p.mother is None
            
            if is_beam:
                curr_pos = [-p.p4.px, -p.p4.py, -p.p4.pz]
            else:
                curr_pos = [0, 0, 0]
            
            for p in track.particles:
                next_pos = [
                    curr_pos[0] + p.p4.px,
                    curr_pos[1] + p.p4.py,
                    curr_pos[2] + p.p4.pz
                ]
                
                label = f"PDG: {p.pdg} ({p.particleType.name})" if len(self.tracks) < 10 else None
                ax.plot([curr_pos[0], next_pos[0]], 
                        [curr_pos[1], next_pos[1]], 
                        [curr_pos[2], next_pos[2]], 
                        label=label, linewidth=2)
                
                # Add text label at the "end" of the track
                if len(self.tracks) < 20: # Only add text labels if we don't have too many tracks
                    # Place label at the end of the particle's path
                    ax.text(next_pos[0], next_pos[1], next_pos[2], f"{p.particleType.name}", fontsize=8)

                curr_pos = next_pos

        ax.set_xlabel('px (GeV)')
        ax.set_ylabel('py (GeV)')
        ax.set_zlabel('pz (GeV)')
        ax.set_title(title)
        if len(self.tracks) < 10:
            ax.legend()
        
        if save_path:
            plt.savefig(save_path)
            print(f"Static plot saved to: {save_path}")

        if show:
            plt.show()
        return fig, ax

    def animate_tracks(self, title="Animated Particle Track Tracing", interval=50, save_path=None):
        """
        Creates an animation of the tracks being traced.
        """
        import matplotlib.pyplot as plt
        from matplotlib.animation import FuncAnimation
        from mpl_toolkits.mplot3d import Axes3D

        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')

        # Find max bounds for the plot
        max_val = 0
        for track in self.tracks:
            p = track.particles[0] if track.particles else None
            if not p: continue
            
            is_beam = p.mother is None
            if is_beam:
                # Beam comes from -p to 0
                max_val = max(max_val, abs(p.p4.px), abs(p.p4.py), abs(p.p4.pz))
            else:
                # Final particles go from 0 to p
                curr = [0, 0, 0]
                for p_part in track.particles:
                    curr[0] += p_part.p4.px
                    curr[1] += p_part.p4.py
                    curr[2] += p_part.p4.pz
                    max_val = max(max_val, abs(curr[0]), abs(curr[1]), abs(curr[2]))

        ax.set_xlim(-max_val, max_val)
        ax.set_ylim(-max_val, max_val)
        ax.set_zlim(-max_val, max_val)
        ax.set_xlabel('px (GeV)')
        ax.set_ylabel('py (GeV)')
        ax.set_zlabel('pz (GeV)')
        ax.set_title(title)

        lines = [ax.plot([], [], [], linewidth=2)[0] for _ in self.tracks]
        # Labels for particles
        texts = [ax.text(0, 0, 0, "", fontsize=8) for _ in self.tracks]

        def init():
            for line in lines:
                line.set_data([], [])
                line.set_3d_properties([])
            for text in texts:
                text.set_text("")
            return lines + texts

        def update(frame):
            # frame goes from 0 to 100 representing percentage of animation completion
            # Split point: Frame 50 is the collision point
            split_frame = 50
            
            for i, track in enumerate(self.tracks):
                p_first = track.particles[0] if track.particles else None
                if not p_first: continue
                
                is_beam = p_first.mother is None
                
                x_data, y_data, z_data = [], [], []
                
                if is_beam:
                    # Beam comes from -p to 0 during frames 0 to split_frame
                    if frame <= split_frame:
                        fraction = frame / float(split_frame)
                    else:
                        fraction = 1.0
                        
                    start_pos = [-p_first.p4.px, -p_first.p4.py, -p_first.p4.pz]
                    end_pos = [
                        start_pos[0] + p_first.p4.px * fraction,
                        start_pos[1] + p_first.p4.py * fraction,
                        start_pos[2] + p_first.p4.pz * fraction
                    ]
                    x_data = [start_pos[0], end_pos[0]]
                    y_data = [start_pos[1], end_pos[1]]
                    z_data = [start_pos[2], end_pos[2]]
                    
                    if frame > 0:
                        texts[i].set_position((end_pos[0], end_pos[1]))
                        texts[i].set_3d_properties(end_pos[2])
                        texts[i].set_text(p_first.particleType.name)
                else:
                    # Final particles grow from 0 starting from split_frame
                    if frame < split_frame:
                        fraction = 0.0
                    else:
                        fraction = (frame - split_frame) / float(100 - split_frame)
                    
                    curr_pos = [0, 0, 0]
                    x_data.append(curr_pos[0])
                    y_data.append(curr_pos[1])
                    z_data.append(curr_pos[2])
                    
                    for p in track.particles:
                        next_pos = [
                            curr_pos[0] + p.p4.px * fraction,
                            curr_pos[1] + p.p4.py * fraction,
                            curr_pos[2] + p.p4.pz * fraction
                        ]
                        x_data.append(next_pos[0])
                        y_data.append(next_pos[1])
                        z_data.append(next_pos[2])
                        
                        if frame >= split_frame:
                            texts[i].set_position((next_pos[0], next_pos[1]))
                            texts[i].set_3d_properties(next_pos[2])
                            texts[i].set_text(p.particleType.name)
                        else:
                            texts[i].set_text("")
                
                lines[i].set_data(x_data, y_data)
                lines[i].set_3d_properties(z_data)
            return lines + texts

        ani = FuncAnimation(fig, update, frames=range(0, 101, 2), init_func=init, 
                            blit=False, interval=interval, repeat=True)
        
        if save_path:
            save_path_str = str(save_path)
            print(f"Saving animation to: {save_path_str}... (this may take a moment)")
            if save_path_str.endswith('.gif'):
                ani.save(save_path_str, writer='pillow')
            else:
                ani.save(save_path_str)
            print(f"Animation saved to: {save_path_str}")

        # Note: In some IDEs, you must keep a reference to 'ani' 
        # to prevent it from being garbage collected.
        plt.show()
        return ani