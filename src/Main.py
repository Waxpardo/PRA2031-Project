from QedSimulation import QedSimulation
from MuonToElectron import MuonToElectron
from ParticleRegistry import ParticleRegistry
from Analysis import SimulatorComparison
from Track import TrackFollowing, TrackVisualizer
from pathlib import Path

OutFile = "OurOutput.txt"
PythiaFile = "mumu_EW.txt"
registry = ParticleRegistry("data/particles.json")

# Define output directory for plots
outputs_dir = Path(__file__).resolve().parent.parent / "outputs"
outputs_dir.mkdir(parents=True, exist_ok=True)

myProcess = MuonToElectron(sqrtS=91.18)
generator = QedSimulation(myProcess, registry)

generator.Run(nEvents=1000, outfile="OurOutput.txt")

# Visualization for selected events
if generator.eventList:
    tracker = TrackFollowing()
    
    # 1. Single Event Visualization (Static)
    last_event = generator.eventList[-1]
    all_particles = last_event.initialParticles + last_event.finalParticles
    tracks_last = tracker.solve(all_particles)
    visualizer_last = TrackVisualizer(tracks_last)
    print(f"\nVisualizing tracks for Event {last_event.id} (Static)...")
    visualizer_last.plot_3d(
        title=f"Static Track Tracing - Event {last_event.id}",
        save_path=outputs_dir / f"event_{last_event.id}_static.png"
    )

    # 2. Single Event Visualization (Animated)
    print(f"Animating tracks for Event {last_event.id}...")
    ani = visualizer_last.animate_tracks(
        title=f"Animated Track Tracing - Event {last_event.id}",
        save_path=outputs_dir / f"event_{last_event.id}_animated.gif"
    )

    # 3. Multiple Events Visualization (Static)
    n_multi = min(5, len(generator.eventList))
    multi_particles = []
    for i in range(n_multi):
        ev = generator.eventList[i]
        multi_particles.extend(ev.initialParticles + ev.finalParticles)
    
    tracks_multi = tracker.solve(multi_particles)
    visualizer_multi = TrackVisualizer(tracks_multi)
    print(f"Visualizing tracks for first {n_multi} events combined...")
    visualizer_multi.plot_3d(
        title=f"Track Tracing - Combined Events (First {n_multi})",
        save_path=outputs_dir / f"combined_events_static.png"
    )

comparison = SimulatorComparison(OutFile, PythiaFile, labels=["cos(theta)"], pdg_to_find=11)
comparison.Run()