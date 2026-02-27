# Mini PYTHIA
A lightweight Python-based particle physics event generator inspired by PYTHIA.

## Table of Contents
- Description
- Background: What is PYTHIA?
- Features
- Installation
- Usage
- Physics Basis
- Statistical Analysis
- Project Structure
- Screenshots
- Contributing
- License
- Contact
- Changelog

---

## Description

Mini PYTHIA is an educational Monte Carlo event generator that simulates the process  
μ⁺ μ⁻ → e⁺ e⁻ at Leading Order (LO) in Quantum Electrodynamics (QED).

It generates events, writes them to file, compares them statistically to a reference sample, and visualizes reconstructed particle tracks in 3D. The project is designed for educational purposes and demonstrates relativistic kinematics, event generation, and statistical validation in a simplified framework.

## Background: What is PYTHIA?

PYTHIA is a widely used high-energy physics event generator developed for simulating particle collisions at experiments such as the Large Hadron Collider (LHC). It models the full chain of events in proton–proton collisions, including:

- Hard scattering processes
- Parton showers
- Hadronization (e.g., Lund string model)
- Particle decays
- Underlying event physics

Mini PYTHIA does **not** aim to reproduce the full complexity of PYTHIA 8. Instead, it focuses on a clean leptonic QED channel to demonstrate core Monte Carlo principles without QCD hadronization or detector effects.

## Features

- Monte Carlo event generation for μ⁺ μ⁻ → e⁺ e⁻
- Relativistic four-vector kinematics
- Event-by-event statistical comparison with reference sample
- Paired hypothesis testing (SciPy + fallback implementation)
- Static and animated 3D track visualization
- Modular and extensible architecture
- Built-in fallback if SciPy is unavailable

## Installation

### Prerequisites

- Python 3.8+
- pip
- Virtual environment recommended

### Setup

1. Clone the repository:

´´´bsh
git clone https://github.com/yourusername/mini-pythia.git
cd mini-pythia
´´´

2. Create and activate a virtual environment:

´´´bsh
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
´´´

3. Install dependencies:

Option A (minimal dependencies):

´´´bsh
python -m pip install -r requirements.txt
´´´

Option B (includes SciPy + Seaborn):

´´´bsh
python -m pip install -r requirements-full.txt
´´´

## Usage

Run the full simulation pipeline:

´´´bsh
python src/Main.py
´´´

For headless environments (no GUI):

´´´bsh
MPLBACKEND=Agg python src/Main.py
´´´

Optional CSV conversion utility:

´´´bsh
python src/ConvertCsv.py
´´´

### Example Workflow

1. Generate events.
2. Output written to `outputs/OurOutput.txt`.
3. Compare with reference sample `outputs/mumu_EW.txt`.
4. Produce statistical test results.
5. Generate static and animated 3D track plots.


## Physics Basis

The simulation models Leading Order QED scattering.

Unlike full-scale generators such as PYTHIA 8, which include QCD dynamics and electroweak interference, Mini PYTHIA isolates the clean leptonic channel μ⁺ μ⁻ → e⁺ e⁻. This allows precise verification of:

- Energy–momentum conservation
- Angular distributions
- Lorentz invariance
- Event-level observable comparison


## Statistical Analysis

`src/Analysis.py` performs an event-by-event paired comparison.

1. Extracts one observable per event (`cos(θ)`).
2. Matches event *i* from both generators.
3. Computes paired differences.
4. Performs:
   - SciPy paired t-test (`scipy.stats.ttest_rel`), or
   - Manual fallback t-statistic with normal approximation.
5. Converts p-value into Gaussian significance (σ).

Interpretation:
- ≥ 5σ → Discovery
- ≥ 3σ → Evidence
- ≥ 2σ → Tension
- < 2σ → Compatible


## Project Structure

´´´
mini-pythia/
│
├── data/
│   ├── particles.json
│   └── processes.json
│
├── outputs/
│   ├── mumu_EW.csv
│   ├── mumu_EW.txt
│   ├── OurOutput.txt
│   └── *.png / *.gif
│
├── src/
│   ├── Main.py
│   ├── QedSimulation.py
│   ├── MuonToElectron.py
│   ├── Track.py
│   ├── Analysis.py
│   ├── Particle.py
│   ├── ParticleClass.py
│   ├── FourVector.py
│   ├── ParticleRegistry.py
│   ├── Process.py
│   ├── PhysicsConstants.py
│   ├── io.py
│   └── ConvertCsv.py
│
├── requirements.txt
├── requirements-full.txt
└── README.md
´´´

## Screenshots

Static track example:

´´´
outputs/event_999_static.png
´´´

Animated track example:

´´´
outputs/event_999_animated.gif
´´´

Combined events visualization:

´´´
outputs/combined_events_static.png
´´´


## Contributing

This project is developed as part of PRA2031: Python Programming.

To contribute:

1. Fork the repository.
2. Create a feature branch.
3. Follow PEP8 style guidelines.
4. Ensure code runs with minimal dependencies.
5. Submit a pull request with a clear description.

Bug reports and feature requests should be submitted via GitHub Issues.


## License

Academic project — not intended for commercial use.

If reused or extended, proper attribution to the original authors is required.


## Contact

For questions or feedback:

- Open a GitHub Issue
- Contact the project maintainers via university email


## Changelog

### v1.0
- Initial event generator
- Statistical comparison module
- 3D track visualization
- SciPy fallback implementation


Last Updated: 27/02/2026
