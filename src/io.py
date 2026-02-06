import json
from pathlib import Path

from src.Particle import ParticleType
from src.Process import Process

def load_particle_types(json_path):
    """Return a dict: name -> ParticleType."""
    data = json.loads(Path(json_path).read_text())
    catalog = {}
    for item in data:
        ptype = ParticleType(
            name=item["name"],
            pdg=item["pdg"],
            particle_class=item["particle_class"],
            mass=item["mass"],
            charge=item["charge"],
            stable=item["stable"],
            decay_modes=item["decay_modes"],
        )
        catalog[ptype.name] = ptype
    return catalog

def load_processes(json_path):
    """Return a dict: name -> Process."""
    data = json.loads(Path(json_path).read_text())
    catalog = {}
    for item in data:
        process = Process.from_dict(item)
        catalog[process.name] = process
    return catalog