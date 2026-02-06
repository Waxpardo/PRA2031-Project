from QedSimulation import QedSimulation
from MuonToElectron import MuonToElectron
from ParticleRegistry import ParticleRegistry

registry = ParticleRegistry("data/particles.json")

myProcess = MuonToElectron(sqrtS=91.18)
generator = QedSimulation(myProcess, registry)
generator.Run(nEvents=5)