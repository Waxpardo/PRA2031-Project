# PRA2031 Particle Physics Project

This repository simulates a toy high-energy physics process (`mu+ mu- -> e+ e-`), compares the generated sample against a reference sample, and visualizes reconstructed tracks.

## What it does

1. Loads particle definitions from JSON.
2. Generates Monte Carlo events.
3. Writes generated events to `outputs/OurOutput.txt`.
4. Compares generated and reference samples with a paired test.
5. Produces static and animated 3D track visualizations.

## File guide

### Main pipeline

- `src/Main.py`
  - Main entry point.
  - Runs generation, visualization, and statistical comparison.

- `src/QedSimulation.py`
  - Event generator for the active process.
  - Creates event objects and writes output text.

- `src/MuonToElectron.py`
  - Physics process implementation (`mu+ mu- -> e+ e-`).

- `src/Track.py`
  - Track reconstruction (`TrackFollowing`) and plotting (`TrackVisualizer`).

- `src/Analysis.py`
  - Reads event files, computes comparison statistics, and plots distributions.
  - Has a built-in fallback if SciPy is unavailable/broken.

### Models and utilities

- `src/Particle.py` - Event-level particle object.
- `src/ParticleClass.py` - Particle metadata model.
- `src/FourVector.py` - Relativistic four-vector and kinematics.
- `src/ParticleRegistry.py` - Particle lookup by name/PDG from JSON.
- `src/Process.py` - Generic process definition.
- `src/PhysicsConstants.py` - Shared physical constants.
- `src/io.py` - JSON loaders for particles/processes.
- `src/ConvertCsv.py` - Converts `outputs/mumu_EW.csv` to `outputs/mumu_EW.txt`.

### Data and outputs

- `data/particles.json` - Particle catalog.
- `data/processes.json` - Process definitions.
- `outputs/mumu_EW.csv` - Reference event sample.
- `outputs/mumu_EW.txt` - Reference sample in text format.
- `outputs/OurOutput.txt` - Generated sample.
- `outputs/event_999_static.png` - Static track plot.
- `outputs/event_999_animated.gif` - Animated track plot.
- `outputs/combined_events_static.png` - Combined-events static plot.

## Statistical method used in the analysis

`src/Analysis.py` compares one observable per event (currently `cos(theta)`) between two generators:

1. Per-event observable extraction
- For each event block in each text file, it selects a particle line (optionally by PDG ID).
- It parses that line's four-momentum `(E, px, py, pz)`.
- It computes `cos(theta) = pz / sqrt(px^2 + py^2 + pz^2)`.

2. Paired comparison
- Events are compared in pairs: event `i` from `OurOutput.txt` is matched with event `i` from `mumu_EW.txt`.
- Let `d_i = x_i - y_i` be the per-event difference in `cos(theta)`.

3. Hypothesis test
- Null hypothesis (`H0`): the mean paired difference is zero.
- Primary implementation: SciPy paired t-test (`scipy.stats.ttest_rel`).
- Fallback implementation (if SciPy is missing/broken):
  - Computes the paired t-statistic from the sample differences.
  - Uses a normal approximation to estimate the two-sided p-value.

4. Significance reporting
- Converts p-value to an equivalent two-sided Gaussian significance (`sigma`).
- Interprets result as:
  - `>= 5σ`: Discovery
  - `>= 3σ`: Evidence
  - `>= 2σ`: Tension
  - `< 2σ`: Compatible

This gives a direct statistical check of whether both generators produce compatible `cos(theta)` distributions event-by-event.

## Installation

Use a virtual environment to avoid system/conda conflicts.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

### Option A (recommended, minimal and robust)

Runs the full project with the built-in stats fallback (no SciPy required):

```bash
python -m pip install -r requirements.txt
```

### Option B (full scientific stack)

Installs SciPy + Seaborn as well:

```bash
python -m pip install -r requirements-full.txt
```

## How to run

From project root:

```bash
python src/Main.py
```

For headless environments (no GUI):

```bash
MPLBACKEND=Agg python src/Main.py
```

Optional conversion utility:

```bash
python src/ConvertCsv.py
```

## Why this avoids the SciPy problem

Your previous error (`ImportError: cannot import name compose_quat`) is an environment binary mismatch. This project now avoids hard-failing on SciPy import by using a fallback statistical implementation in `src/Analysis.py`, and the README uses isolated, pinned dependencies to keep installs reproducible for other users.

## Notes

- Use `src/Main.py` as the canonical entry point.
- Keep generated artifacts in `outputs/`.
