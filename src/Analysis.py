import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import norm
from pathlib import Path
import re


class SimulatorComparison:
    def __init__(self, genOurFile, genPythiaFile, labels=None):

        self.genOur = self._deserialize_file(genOurFile)
        self.genPythia = self._deserialize_file(genPythiaFile)

        self.genOur = np.array(self.genOur)
        self.genPythia = np.array(self.genPythia)

        if labels is not None:
            self.labels = labels
        else:
            self.labels = ["Observable"]

        self.delta = None

    def _deserialize_file(self, filename):

        project_root = Path(__file__).resolve().parent.parent

        filepath = project_root / "outputs" / filename

        if not filepath.exists():
            raise FileNotFoundError(f"Could not find file: {filepath}")

        observables = []

        with open(filepath, "r") as file:
            lines = file.readlines()

        current_event = []

        for line in lines:
            line = line.strip()

            if line.startswith("Event"):
                if current_event:
                    obs = self._extract_observable(current_event)
                    observables.append(obs)
                    current_event = []
            elif line:
                current_event.append(line)

        if current_event:
            obs = self._extract_observable(current_event)
            observables.append(obs)

        return observables

    def _extract_observable(self, event_lines):

        final_particle_line = event_lines[-2]

        numbers = re.findall(r"[-+]?\d*\.\d+|\d+", final_particle_line)

        if len(numbers) < 4:
            raise ValueError(f"Could not parse momentum from line:\n{final_particle_line}")

        E, px, py, pz = map(float, numbers[:4])

        momentum_mag = np.sqrt(px ** 2 + py ** 2 + pz ** 2)

        if momentum_mag == 0:
            return 0.0

        cos_theta = pz / momentum_mag

        return cos_theta

    def compute_difference(self):
        self.delta = self.genOur - self.genPythia
        return self.delta

    def _pvalue_to_sigma(self, p_val):
        if p_val <= 0:
            return np.inf
        return norm.isf(p_val / 2)

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

    def paired_t_test(self):
        t_stat, p_val = stats.ttest_rel(self.genOur, self.genPythia)

        sigma, level, significant = self._interpret_significance(p_val)

        return {
            "test": "Paired t-test",
            "t_stat": t_stat,
            "p_value": p_val,
            "sigma": sigma,
            "level": level,
            "significant": significant
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
        sns.histplot(self.genOur, label="Our Generator", kde=True, stat="density")
        sns.histplot(self.genPythia, label="Pythia", kde=True, stat="density")
        plt.legend()
        plt.xlabel(self.labels[0])
        plt.title("Generator Comparison")
        plt.show()

    def Run(self):

        print("\nReading event files...")
        print(f"Our generator events   : {len(self.genOur)}")
        print(f"Pythia generator events: {len(self.genPythia)}")

        if len(self.genOur) != len(self.genPythia):
            raise ValueError("Event samples must have same length for paired test.")

        print("\nRunning paired t-test...\n")

        result = self.paired_t_test()
        self.print_result(result)

        print("\nPlotting distributions...")
        self.plot_distributions()
