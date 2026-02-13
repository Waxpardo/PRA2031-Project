from QedSimulation import QedSimulation
from MuonToElectron import MuonToElectron
from ParticleRegistry import ParticleRegistry
from Analysis import SimulatorComparison

OutFile = "OurOutput.txt"
PythiaFile = "OurOutput.txt"
registry = ParticleRegistry("data/particles.json")

myProcess = MuonToElectron(sqrtS=91.18)
generator = QedSimulation(myProcess, registry)

generator.Run(nEvents=1000, outfile="OurOutput.txt")

comparison = SimulatorComparison(OutFile, PythiaFile)
comparison.Run()