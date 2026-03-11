import math
import re
from pathlib import Path
from statistics import NormalDist

import matplotlib.pyplot as plt
import numpy as np

try:
    from scipy import stats as scipy_stats
except Exception:
    scipy_stats = None

try:
    import seaborn as sns
except Exception:
    sns = None


class SimulatorComparison:
    """
    Compares the physical output of a custom particle generator
    against the industry-standard PYTHIA generator.
    """

    def __init__(self, genOurFile, genPythiaFile, labels=None, pdgToFind=None):
        # Load the raw event data from text files into memory
        self.genOur = self.DeserializeFile(genOurFile, pdgToFind)
        self.genPythia = self.DeserializeFile(genPythiaFile, pdgToFind)

        # Convert to NumPy arrays to allow for fast vector math
        # and statistical operations.
        self.genOur = np.array(self.genOur)
        self.genPythia = np.array(self.genPythia)

        # Labels for the X-axis of the final comparison plots
        if labels is not None:
            self.labels = labels
        else:
            self.labels = ["Observable"]

        self.delta = None

    def DeserializeFile(self, fileName, pdgToFind=None):
        """
        Reads a simulation output file and extracts specific particle data.
        """
        # Finds the directory where the code is located to build a file path
        projectRoot = Path(__file__).resolve().parent.parent
        filePath = projectRoot / "outputs" / fileName

        if not filePath.exists():
            raise FileNotFoundError(f"Could not find file: {filePath}")

        observables = []

        with open(filePath, "r") as file:
            lines = file.readlines()

        currentEvent = []

        # Particles are grouped into 'Events' (one 'collision' per event)
        for line in lines:
            line = line.strip()

            if line.startswith("Event"):
                if currentEvent:
                    # Process the data for the event just finished
                    obs = self.ExtractObservable(currentEvent, pdgToFind)
                    observables.append(obs)
                    currentEvent = []
            elif line:
                currentEvent.append(line)

        # Catch the last event in the file
        if currentEvent:
            obs = self.ExtractObservable(currentEvent, pdgToFind)
            observables.append(obs)

        return observables

    def ExtractObservable(self, eventLines, pdgToFind=None):
        """
        Calculates a physical value (cos theta) from a specific particle in an event.
        """
        selectedLine = None

        # PDG IDs are universal numeric codes for particles (e.g., 11 for electron, 13 for muon)
        if pdgToFind:
            for line in reversed(eventLines):
                parts = line.split("|")
                if len(parts) >= 2:
                    pdgStr = parts[1].strip()
                    if pdgStr == str(pdgToFind):
                        selectedLine = line
                        break

        # Default to the second-to-last line if no specific particle ID is given
        if selectedLine is None:
            selectedLine = eventLines[-2]

        # The line prefix contains the event ID and PDG code, so only the
        # final four numeric values belong to the rendered four-vector.
        numbers = re.findall(r"[-+]?\d*\.\d+|\d+", selectedLine)

        if len(numbers) < 4:
            raise ValueError(f"Could not parse momentum from line:\n{selectedLine}")

        # E=Energy, px/py/pz = Momentum components in 3D space
        _, px, py, pz = map(float, numbers[-4:])

        # Calculate the total length of the momentum vector (the 'speed' of the particle)
        momentumMag = np.sqrt(px ** 2 + py ** 2 + pz ** 2)

        if momentumMag == 0:
            return 0.0

        # Cos(Theta) tells us the angle of the particle relative to the beam axis (Z).
        # It ranges from -1 (backward) to 1 (forward).
        cosTheta = pz / momentumMag

        return cosTheta

    def ComputeDifference(self):
        """Calculates the direct gap between our generator and Pythia."""
        self.delta = self.genOur - self.genPythia
        return self.delta

    def PvalueToSigma(self, pVal):
        """
        Converts a probability (p-value) into 'Sigma'.
        In physics, 5-sigma is the 'Gold Standard' for claiming a discovery.
        """
        if pVal <= 0:
            return np.inf
        return NormalDist().inv_cdf(1 - (pVal / 2))

    def InterpretSignificance(self, pVal):
        """Translates statistical numbers into physics-standard terminology."""
        sigma = self.PvalueToSigma(pVal)

        if sigma >= 5:
            level = "5σ (Discovery)"
            significant = True
        elif sigma >= 3:
            level = "3σ (Evidence)"
            significant = True
        elif sigma >= 2:
            level = "2σ (Tension)"
            significant = False
        else:
            level = "< 2σ (Compatible)"
            significant = False

        return sigma, level, significant

    def ManualPairedTTest(self):
        """
        Fallback paired t-test when SciPy is unavailable.
        Uses the usual t-statistic and a normal approximation for the p-value.
        """
        delta = self.ComputeDifference()
        nObs = len(delta)

        if nObs < 2:
            raise ValueError("Need at least two paired observations for a t-test.")

        meanDelta = float(np.mean(delta))
        stdDelta = float(np.std(delta, ddof=1))

        if stdDelta == 0.0:
            if meanDelta == 0.0:
                return 0.0, 1.0, "Manual fallback (zero variance)"
            return np.inf, 0.0, "Manual fallback (zero variance)"

        tStat = meanDelta / (stdDelta / math.sqrt(nObs))
        pVal = math.erfc(abs(tStat) / math.sqrt(2))
        return tStat, pVal, "Manual fallback (normal approximation)"

    def PairedTTest(self):
        """
        Checks if the mean difference between the two simulators is zero.
        Used to see if our generator has a 'bias' compared to Pythia.
        """
        backend = "SciPy"
        if scipy_stats is not None:
            try:
                tStat, pVal = scipy_stats.ttest_rel(self.genOur, self.genPythia)
            except Exception:
                tStat, pVal, backend = self.ManualPairedTTest()
        else:
            tStat, pVal, backend = self.ManualPairedTTest()

        sigma, level, significant = self.InterpretSignificance(pVal)

        return {
            "test": "Paired t-test",
            "tStat": tStat,
            "pVal": pVal,
            "sigma": sigma,
            "level": level,
            "significant": significant,
            "backend": backend,
        }
    def KSTest(self):
        stat, pVal = stats.ks_2samp(self.genOur, self.genPythia)
        sigma, level, significant = self.InterpretSignificance(pVal)
        return {"test": "KS Test", "tStat": stat, "pVal": pVal,
                "sigma": sigma, "level": level, "significant": significant}
        
    def PrintResult(self, result):
        """Formats the statistical findings for the console."""
        print("=" * 60)
        print(result["test"])
        print("-" * 60)
        print(f"backend      : {result['backend']}")
        print(f"t-statistic  : {result['tStat']:.3f}")
        print(f"p-value      : {result['pVal']:.3e}")
        print(f"significance : {result['sigma']:.2f} σ")
        print(f"interpretation: {result['level']}")

        if result["significant"]:
            print("→ Null hypothesis rejected (Generators are DIFFERENT)")
        else:
            print("→ Null hypothesis not rejected (Generators are CONSISTENT)")

    def PlotDistributions(self, show=True, savePath=None):
        """Creates a visual overlay of both generators to see if the shapes match."""
        fig, ax = plt.subplots(figsize=(10, 6))

        if sns is not None:
            # KDE (Kernel Density Estimate) creates a smooth line over the histogram bars.
            sns.histplot(self.genOur, label="Our Generator", kde=True, stat="density", ax=ax)
            sns.histplot(self.genPythia, label="Pythia", kde=True, stat="density", ax=ax)
        else:
            bins = np.linspace(-1.0, 1.0, 31)
            ax.hist(self.genOur, bins=bins, density=True, alpha=0.5, label="Our Generator")
            ax.hist(self.genPythia, bins=bins, density=True, alpha=0.5, label="Pythia")

        ax.legend()
        ax.set_xlabel(self.labels[0])
        ax.set_ylabel("Density")
        ax.set_title("Generator Comparison")

        if savePath is not None:
            fig.savefig(savePath, dpi=200, bbox_inches="tight")
            print(f"Distribution plot saved to: {savePath}")

        if show:
            plt.show()
        else:
            plt.close(fig)

        return fig, ax

    def Run(self):
        """The main execution loop for the comparison."""
        print("\nReading event files...")
        print(f"Our generator events   : {len(self.genOur)}")
        print(f"Pythia generator events: {len(self.genPythia)}")

        # A paired test requires an identical number of 'shots' from each generator.
        if len(self.genOur) != len(self.genPythia):
            raise ValueError("Event samples must have same length for paired test.")

        print("\nRunning paired t-test...\n")

        result = self.PairedTTest()
        self.PrintResult(result)

        print("\nPlotting distributions...")
        projectRoot = Path(__file__).resolve().parent.parent
        plotPath = projectRoot / "outputs" / "generator_comparison.png"
        self.PlotDistributions(savePath=plotPath)
