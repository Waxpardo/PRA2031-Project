from QedSimulation import QedSimulation
from MuonToElectron import MuonToElectron
from ParticleRegistry import ParticleRegistry
from Analysis import SimulatorComparison
from Track import TrackFollowing, TrackVisualizer
from pathlib import Path

"""
MAIN CONTROL HUB
This script integrates all subsystems: 
1. Physics Simulation (QED)
2. Particle Tracking (Trajectory calculation)
3. Visualization (3D plotting)
4. Statistical Analysis (Validation against PYTHIA)
"""

# File names for data storage
ourFile = "OurOutput.txt"
pythiaFile = "mumu_EW.txt"

# The ParticleRegistry acts like a library, containing physical constants
# for every particle (mass, charge, etc.) stored in a JSON file.
registry = ParticleRegistry("data/particles.json")

# Ensure the 'outputs' folder exists for saving graphs and animations
outputsDir = Path(__file__).resolve().parent.parent / "outputs"
outputsDir.mkdir(parents=True, exist_ok=True)

# 'sqrtS' represents the Center-of-Mass Energy in GeV.
# 91.18 GeV is the mass of the Z-boson, a common energy for particle colliders.
myProcess = MuonToElectron(sqrtS=91.18)

# Initialize the Quantum Electrodynamics (QED) simulation engine
generator = QedSimulation(myProcess, registry)

# Run the simulation for 1,000 unique collision events
# In a deterministic setup, this will yield the same result every time.
generator.Run(nEvents=1000, outFile="OurOutput.txt")

"""
TRACKING AND VISUALIZATION
Calculates the paths particles take as they move through the detector space.
"""

if generator.eventList:
    # TrackFollowing calculates the 'flight paths' based on momentum vectors
    tracker = TrackFollowing()

    # 1. Single Event Visualization (Static 3D Image)
    # This shows where particles flew immediately after a single collision.
    lastEvent = generator.eventList[-1]
    allParticles = lastEvent.initialParticles + lastEvent.finalParticles
    tracksLast = tracker.Solve(allParticles)
    visualizerLast = TrackVisualizer(tracksLast)

    print(f"\nVisualizing tracks for Event {lastEvent.id} (Static)...")
    visualizerLast.Plot3d(
        title=f"Static Track Tracing - Event {lastEvent.id}",
        savePath=outputsDir / f"event_{lastEvent.id}_static.png"
    )

    # 2. Single Event Visualization (Animated GIF)
    # This creates a movie showing the particles expanding outward from the center.
    print(f"Animating tracks for Event {lastEvent.id}...")
    ani = visualizerLast.AnimateTracks(
        title=f"Animated Track Tracing - Event {lastEvent.id}",
        savePath=outputsDir / f"event_{lastEvent.id}_animated.gif"
    )

    # 3. Multiple Events Visualization (Static)
    # Overlays several collisions to show the general 'shape' of the physics process.
    nMulti = min(5, len(generator.eventList))
    multiParticles = []
    for i in range(nMulti):
        ev = generator.eventList[i]
        multiParticles.extend(ev.initialParticles + ev.finalParticles)

    tracksMulti = tracker.Solve(multiParticles)
    visualizerMulti = TrackVisualizer(tracksMulti)

    print(f"Visualizing tracks for first {nMulti} events combined...")
    visualizerMulti.Plot3d(
        title=f"Track Tracing - Combined Events (First {nMulti})",
        savePath=outputsDir / "combined_events_static.png"
    )

"""
CROSS-VALIDATION
Compares our custom generator's math against the PYTHIA physics engine.
PDG 11 refers to Electrons; we are checking if their angular distribution matches.
"""
# pdgToFind=11 tells the analyzer to specifically look for Electron data
comparison = SimulatorComparison(ourFile, pythiaFile, labels=["cos(theta)"], pdgToFind=11)
comparison.Run()