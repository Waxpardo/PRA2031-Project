import json
from pathlib import Path
from ParticleClass import ParticleClass

class ParticleRegistry:
    """
    A management system that loads and stores the physical properties
    of particles from a central JSON file.
    """
    def __init__(self, jsonPath):
        # catalogByName: Allows looking up a particle using its string name (e.g., "muon")
        self.catalogByName = {}
        # catalogByPdg: Allows looking up a particle using its ID number (e.g., 13)
        self.catalogByPdg = {}
        self.LoadParticles(jsonPath)

    def LoadParticles(self, jsonPath):
        """
        Parses the JSON file and populates the internal lookup dictionaries.
        """
        # Finds the file on your computer, handling different folder structures
        pathObj = Path(jsonPath)
        if not pathObj.is_absolute():
            # Looks starting from the project root if a relative path is given
            pathObj = Path(__file__).parent.parent / jsonPath

        if not pathObj.exists():
            raise FileNotFoundError(f"Could not find particle data at: {pathObj.absolute()}")

        # Reads the text from the file and converts it into a Python list
        data = json.loads(pathObj.read_text())
        for item in data:
            # Create an instance of ParticleClass for every entry in the JSON
            pType = ParticleClass(
                name=item["name"],
                pdg=item["pdg"],
                particle_class=item["particle_class"],
                mass=item["mass"],
                charge=item["charge"],
                stable=item["stable"],
                decay_modes=item["decay_modes"]
            )
            # Store the particle object in both dictionaries for easy access
            self.catalogByName[pType.name] = pType
            self.catalogByPdg[pType.pdg] = pType

    def GetByPdg(self, pdg):
        """Returns the particle data matching a specific numeric ID."""
        return self.catalogByPdg.get(pdg)

    def GetByName(self, name):
        """Returns the particle data matching a specific text name."""
        return self.catalogByName.get(name)