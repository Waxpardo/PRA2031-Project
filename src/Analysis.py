import math
import re
from pathlib import Path
from statistics import NormalDist

import matplotlib.pyplot as plt
import numpy as np

try:
    import seaborn as sns
except Exception:
    sns = None

try:
    from scipy import stats as scipy_stats
except Exception:
    scipy_stats = None


STANDARD_NORMAL = NormalDist()


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
        self.genOur = np.array(self.genOur, dtype=float)
        self.genPythia = np.array(self.genPythia, dtype=float)

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

        with open(filePath, "r", encoding="utf-8") as file:
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

        # Use Regular Expressions to find numbers (Energy and Momentum) in the string
        numbers = re.findall(r"[-+]?\d*\.\d+|\d+", selectedLine)

        if len(numbers) < 4:
            raise ValueError(f"Could not parse momentum from line:\\n{selectedLine}")

        # E=Energy, px/py/pz = Momentum components in 3D space
        energy, px, py, pz = map(float, numbers[:4])

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

    def _two_sided_normal_pvalue(self, stat):
        return max(0.0, min(1.0, 2.0 * (1.0 - STANDARD_NORMAL.cdf(abs(float(stat))))))

    def _sanitize_result(self, stat, pVal):
        stat = float(stat)
        pVal = float(pVal)

        if np.isnan(stat) or np.isnan(pVal):
            delta = self.ComputeDifference()
            if np.allclose(delta, 0.0):
                return 0.0, 1.0

        return stat, pVal

    def _manual_paired_t_test(self):
        delta = self.ComputeDifference()
        n = delta.size

        if n < 2:
            raise ValueError("At least two paired events are required for the t-test.")

        meanDelta = float(np.mean(delta))
        stdDelta = float(np.std(delta, ddof=1))

        if np.isclose(stdDelta, 0.0):
            if np.isclose(meanDelta, 0.0):
                return 0.0, 1.0
            return math.copysign(math.inf, meanDelta), 0.0

        tStat = meanDelta / (stdDelta / np.sqrt(n))
        pVal = self._two_sided_normal_pvalue(tStat)
        return tStat, pVal

    def _kolmogorov_pvalue(self, dStat, n1, n2):
        if dStat <= 0:
            return 1.0

        effectiveN = math.sqrt((n1 * n2) / (n1 + n2))
        if effectiveN == 0:
            return 1.0

        lam = (effectiveN + 0.12 + 0.11 / effectiveN) * dStat
        total = 0.0

        for k in range(1, 200):
            term = math.exp(-2.0 * (k ** 2) * (lam ** 2))
            total += ((-1) ** (k - 1)) * term
            if term < 1e-12:
                break

        return max(0.0, min(1.0, 2.0 * total))

    def _manual_ks_test(self):
        sample1 = np.sort(self.genOur)
        sample2 = np.sort(self.genPythia)
        n1 = sample1.size
        n2 = sample2.size

        if n1 == 0 or n2 == 0:
            raise ValueError("Both samples must contain at least one event for the KS test.")

        combined = np.concatenate((sample1, sample2))
        cdf1 = np.searchsorted(sample1, combined, side="right") / n1
        cdf2 = np.searchsorted(sample2, combined, side="right") / n2
        dStat = float(np.max(np.abs(cdf1 - cdf2)))
        pVal = self._kolmogorov_pvalue(dStat, n1, n2)
        return dStat, pVal

    def PvalueToSigma(self, pVal):
        """
        Converts a probability (p-value) into 'Sigma'.
        In physics, 5-sigma is the 'Gold Standard' for claiming a discovery.
        """
        if np.isnan(pVal):
            return np.nan
        if pVal <= 0:
            return np.inf
        if pVal >= 1:
            return 0.0

        tailProbability = 1.0 - pVal / 2.0
        tailProbability = min(math.nextafter(1.0, 0.0), tailProbability)
        tailProbability = max(math.nextafter(0.0, 1.0), tailProbability)
        return STANDARD_NORMAL.inv_cdf(tailProbability)

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

    def PairedTTest(self):
        """
        Checks if the mean difference between the two simulators is zero.
        Used to see if our generator has a 'bias' compared to Pythia.
        """
        implementation = "Fallback"

        if scipy_stats is not None:
            try:
                tStat, pVal = scipy_stats.ttest_rel(self.genOur, self.genPythia)
                implementation = "SciPy"
            except Exception:
                tStat, pVal = self._manual_paired_t_test()
        else:
            tStat, pVal = self._manual_paired_t_test()

        tStat, pVal = self._sanitize_result(tStat, pVal)
        sigma, level, significant = self.InterpretSignificance(pVal)

        return {
            "test": "Paired t-test",
            "tStat": tStat,
            "pVal": pVal,
            "sigma": sigma,
            "level": level,
            "significant": significant,
            "implementation": implementation,
        }

    def KSTest(self):
        """Compares the full observable distributions of both generators."""
        implementation = "Fallback"

        if scipy_stats is not None:
            try:
                result = scipy_stats.ks_2samp(self.genOur, self.genPythia)
                dStat, pVal = result.statistic, result.pvalue
                implementation = "SciPy"
            except Exception:
                dStat, pVal = self._manual_ks_test()
        else:
            dStat, pVal = self._manual_ks_test()

        dStat, pVal = self._sanitize_result(dStat, pVal)
        sigma, level, significant = self.InterpretSignificance(pVal)

        return {
            "test": "Kolmogorov-Smirnov test",
            "dStat": dStat,
            "pVal": pVal,
            "sigma": sigma,
            "level": level,
            "significant": significant,
            "implementation": implementation,
        }

    def PrintResult(self, result):
        """Formats the statistical findings for the console."""
        print("=" * 60)
        print(result["test"])
        print("-" * 60)

        if "tStat" in result:
            print(f"statistic    : {result['tStat']:.4f}")
        elif "dStat" in result:
            print(f"statistic    : {result['dStat']:.4f}")

        print(f"p-value      : {result['pVal']:.3e}")
        print(f"significance : {result['sigma']:.2f} σ")
        print(f"interpretation: {result['level']}")
        print(f"implementation: {result.get('implementation', 'N/A')}")

        if result["significant"]:
            print("→ Null hypothesis rejected (Generators are DIFFERENT)")
        else:
            print("→ Null hypothesis not rejected (Generators are CONSISTENT)")

    def PlotDistributions(self):
        """Creates a visual overlay of both generators to see if the shapes match."""
        plt.figure()

        # Seaborn is optional; the base requirements only guarantee Matplotlib.
        if sns is not None:
            sns.histplot(self.genOur, label="Our Generator", kde=True, stat="density")
            sns.histplot(self.genPythia, label="Pythia", kde=True, stat="density")
        else:
            bins = 30
            plt.hist(self.genOur, bins=bins, density=True, alpha=0.5, label="Our Generator")
            plt.hist(self.genPythia, bins=bins, density=True, alpha=0.5, label="Pythia")

        plt.legend()
        plt.xlabel(self.labels[0])
        plt.title("Generator Comparison")
        plt.tight_layout()
        plt.show()

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
        self.PlotDistributions()
