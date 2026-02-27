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
    from scipy.stats import norm as scipy_norm
except Exception:
    scipy_stats = None
    scipy_norm = None


class SimulatorComparison:
    def __init__(self, genOurFile, genPythiaFile, labels=None, pdg_to_find=None):
        self.genOur = np.array(self._deserialize_file(genOurFile, pdg_to_find), dtype=float)
        self.genPythia = np.array(self._deserialize_file(genPythiaFile, pdg_to_find), dtype=float)

        if labels is not None:
            self.labels = labels
        else:
            self.labels = ["Observable"]

        self.delta = None

    def _deserialize_file(self, filename, pdg_to_find=None):
        project_root = Path(__file__).resolve().parent.parent
        filepath = project_root / "outputs" / filename

        if not filepath.exists():
            raise FileNotFoundError(f"Could not find file: {filepath}")

        observables = []
        current_event = []

        with open(filepath, "r", encoding="utf-8") as file:
            for raw_line in file:
                line = raw_line.strip()
                if line.startswith("Event"):
                    if current_event:
                        observables.append(self._extract_observable(current_event, pdg_to_find))
                        current_event = []
                elif line:
                    current_event.append(line)

        if current_event:
            observables.append(self._extract_observable(current_event, pdg_to_find))

        return observables

    def _extract_observable(self, event_lines, pdg_to_find=None):
        selected_line = None

        if pdg_to_find is not None:
            for line in reversed(event_lines):
                parts = line.split("|")
                if len(parts) >= 2 and parts[1].strip() == str(pdg_to_find):
                    selected_line = line
                    break

        if selected_line is None:
            selected_line = event_lines[-2] if len(event_lines) >= 2 else event_lines[-1]

        # Parse only the four-momentum block to avoid picking event/PDG columns.
        match = re.search(
            r"\(E:\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?),\s*"
            r"px:\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?),\s*"
            r"py:\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?),\s*"
            r"pz:\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\)",
            selected_line,
        )
        if match is None:
            raise ValueError(f"Could not parse four-momentum from line:\n{selected_line}")

        _, px, py, pz = map(float, match.groups())

        momentum_mag = np.sqrt(px ** 2 + py ** 2 + pz ** 2)
        if momentum_mag == 0:
            return 0.0

        cos_theta = pz / momentum_mag
        return float(cos_theta)

    def compute_difference(self):
        self.delta = self.genOur - self.genPythia
        return self.delta

    def _normal_two_sided_pvalue(self, z_value):
        return 2.0 * (1.0 - NormalDist().cdf(abs(float(z_value))))

    def _pvalue_to_sigma(self, p_val):
        if p_val <= 0:
            return np.inf
        if scipy_norm is not None:
            return float(scipy_norm.isf(p_val / 2.0))
        return float(NormalDist().inv_cdf(1.0 - (p_val / 2.0)))

    def _interpret_significance(self, p_val):
        sigma = self._pvalue_to_sigma(p_val)

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

    def _paired_t_test_fallback(self):
        # Fallback when SciPy is unavailable/broken: t-statistic + normal approximation.
        differences = self.genOur - self.genPythia
        n = differences.size
        if n < 2:
            raise ValueError("Need at least two events for paired t-test.")

        mean_diff = float(np.mean(differences))
        std_diff = float(np.std(differences, ddof=1))

        if std_diff == 0.0:
            if mean_diff == 0.0:
                return 0.0, 1.0
            return np.sign(mean_diff) * np.inf, 0.0

        t_stat = mean_diff / (std_diff / np.sqrt(n))
        p_val = self._normal_two_sided_pvalue(t_stat)
        return float(t_stat), float(p_val)

    def paired_t_test(self):
        if self.genOur.shape != self.genPythia.shape:
            raise ValueError("Event samples must have same length for paired test.")

        if scipy_stats is not None:
            t_stat, p_val = scipy_stats.ttest_rel(self.genOur, self.genPythia)
            test_name = "Paired t-test (SciPy)"
        else:
            t_stat, p_val = self._paired_t_test_fallback()
            test_name = "Paired t-test (normal approximation fallback)"

        sigma, level, significant = self._interpret_significance(p_val)

        return {
            "test": test_name,
            "t_stat": float(t_stat),
            "p_value": float(p_val),
            "sigma": sigma,
            "level": level,
            "significant": significant,
        }

    def print_result(self, result):
        print("=" * 60)
        print(result["test"])
        print("-" * 60)
        print(f"p-value      : {result['p_value']:.3e}")
        print(f"significance : {result['sigma']:.2f} σ")
        print(f"interpretation: {result['level']}")

        if result["significant"]:
            print("→ Null hypothesis rejected")
        else:
            print("→ Null hypothesis not rejected")

    def plot_distributions(self):
        if sns is not None:
            sns.histplot(self.genOur, label="Our Generator", kde=True, stat="density")
            sns.histplot(self.genPythia, label="Pythia", kde=True, stat="density")
        else:
            plt.hist(self.genOur, bins=40, alpha=0.5, density=True, label="Our Generator")
            plt.hist(self.genPythia, bins=40, alpha=0.5, density=True, label="Pythia")

        plt.legend()
        plt.xlabel(self.labels[0])
        plt.title("Generator Comparison")
        plt.show()

    def Run(self):
        print("\nReading event files...")
        print(f"Our generator events   : {len(self.genOur)}")
        print(f"Pythia generator events: {len(self.genPythia)}")
        print(f"Stats backend          : {'SciPy' if scipy_stats is not None else 'NumPy fallback'}")
        print(f"Plot backend           : {'seaborn' if sns is not None else 'matplotlib'}")

        if len(self.genOur) != len(self.genPythia):
            raise ValueError("Event samples must have same length for paired test.")

        print("\nRunning paired t-test...\n")
        result = self.paired_t_test()
        self.print_result(result)

        print("\nPlotting distributions...")
        self.plot_distributions()
