import json
from pathlib import Path
from ParticleClass import ParticleClass

class ParticleRegistry:
    def __init__(self, jsonPath):
        self.catalogByName = {}
        self.catalogByPdg = {}
        self.LoadParticles(jsonPath)

    def LoadParticles(self, jsonPath):
        # Resolve the path to handle relative directory issues
        pathObj = Path(jsonPath)
        if not pathObj.is_absolute():
            # If relative, assume it starts from the project root
            pathObj = Path(__file__).parent.parent / jsonPath

        if not pathObj.exists():
            raise FileNotFoundError(f"Could not find particle data at: {pathObj.absolute()}")

        data = json.loads(pathObj.read_text())
        for item in data:
            pType = ParticleClass(
                name=item["name"],
                pdg=item["pdg"],
                particle_class=item["particle_class"],
                mass=item["mass"],
                charge=item["charge"],
                stable=item["stable"],
                decay_modes=item["decay_modes"]
            )
            self.catalogByName[pType.name] = pType
            self.catalogByPdg[pType.pdg] = pType

    def GetByPdg(self, pdg):
        return self.catalogByPdg.get(pdg)

    def GetByName(self, name):
        return self.catalogByName.get(name)