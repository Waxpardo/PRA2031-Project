import json
from pathlib import Path

from src.ParticleClass import ParticleClass
from src.Process import Process


def _normalize_decay_modes(decay_modes):
    if decay_modes is None:
        return []
    if not isinstance(decay_modes, list):
        raise TypeError("decay_modes must be a list")

    normalized = []
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

        normalized.append({"br": mode["br"], "products": products})

    return normalized


def load_particle_types(json_path):
    """Return a dict: particle name -> ParticleClass."""
    data = json.loads(Path(json_path).read_text(encoding="utf-8"))
    catalog = {}
    for item in data:
        ptype = ParticleClass(
            name=item["name"],
            pdg=item["pdg"],
            particle_class=item["particle_class"],
            mass=item["mass"],
            charge=item["charge"],
            stable=item["stable"],
            decay_modes=_normalize_decay_modes(item.get("decay_modes", [])),
        )
        catalog[ptype.name] = ptype
    return catalog


def load_processes(json_path):
    """Return a dict: process name -> Process."""
    data = json.loads(Path(json_path).read_text(encoding="utf-8"))
    catalog = {}
    for item in data:
        process = Process.from_dict(item)
        catalog[process.name] = process
    return catalog
