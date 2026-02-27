from pathlib import Path

from src.io import load_particle_types, load_processes


def main():
    project_root = Path(__file__).resolve().parent
    particles_path = project_root / "data" / "particles.json"
    processes_path = project_root / "data" / "processes.json"

    particle_types = load_particle_types(particles_path)
    processes = load_processes(processes_path)

    print(f"Loaded {len(particle_types)} particle types and {len(processes)} processes.")
    for process in processes.values():
        incoming = " + ".join(process.incoming)
        outgoing = " + ".join(process.outgoing)
        print(f"- {process.name}: {incoming} -> {outgoing} ({process.model})")


if __name__ == "__main__":
    main()
