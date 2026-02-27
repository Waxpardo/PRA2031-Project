Mini Pythia: Muon-Antimuon Collision Simulator
PRA2031 - Research Project 

1. Project Overview:
Mini Pythia is a lightweight event generator designed to simulate high-energy particle collisions, specifically focusing on muon-antimuon (μ^+ μ^-) interactions. Inspired by the industry-standard Pythia 8 framework, this project implements the core Monte Carlo methods required to calculate cross-sections and final-state kinematics for future muon collider research.

2. Why "Mini Pythia"?
While the full Pythia 8 package handles hundreds of particle types and complex QCD hadronization, Mini Pythia is optimized for the "clean" environment of a muon collider.
Focus: Electroweak interactions (Z^0 / γ exchange).
Scope: Accurate modeling of the Z-boson resonance peak (91.18 GeV).
Efficiency: Lightweight Python implementation compared to the original C++ library.

3. Physics ImplementationThis simulator accounts for the following physical phenomena:
Relativistic Kinematics: Full 4-vector conservation (E^2 = p^2 + m^2) for incoming and outgoing particles.
Breit-Wigner Resonance: Modeling the Z^0 propagator to determine the probability of interaction as a function of center-of-mass energy (sqrt{s}).
Angular Distribution: Implementation of the (1 + cos^2{θ}) differential cross-section for fermion-antifermion scattering.Monte Carlo Integration: Using rejection sampling to generate realistic event distributions.

4. Installation & Usage:
