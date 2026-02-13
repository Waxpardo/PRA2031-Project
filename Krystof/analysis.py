import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import norm

class SimulatorComparison:
    def __init__(self, genOur, genPythia, labels=None):
        self.genOur = np.array(genOur)
        self.genPythia = np.array(genPythia)
        if labels is not None:
            self.labels = labels
        else:
            if self.genOur.ndim > 1:
                self.labels = [f"Var{i}" for i in range(self.genOur.shape[1])]
            else:
                self.labels = ["Observable"]
                self.delta = None

    #computing differences (delta) in datasets for same observables
    def compute_difference(self):
        self.delta = self.genOur - self.genPythia
        return self.delta

    def _interpret_pvalue(self, p_val, alpha):
        significant = p_val < alpha
        if significant:
            conclusion = f"Significant difference (p < {alpha})"
        else:
            conclusion = f"No significant difference (p ≥ {alpha})"

        return significant, conclusion

    def _pvalue_to_sigma(self, p_val):
        if p_val <= 0:
            return np.inf
        return norm.isf(p_val / 2)
    

    #paired t-test statistical analysis. Independent data sets &  same event
    def paired_t_test(self):
        if self.delta is None:
            self.compute_difference()

        t_stat, p_val = stats.ttest_rel(self.genOur, self.genPythia, axis=0)

        sigma, level, significant = self._interpret_significance(p_val)

        return {
            "test": "Paired t-test",
            "t_stat": t_stat,
            "p_value": p_val,
            "sigma": sigma,
            "level": level,
            "significant": significant
        }


    """ #Wilcoxon signed-rank test
    def wilcoxon_test(self, alpha=0.05):
        if self.delta is None:
            self.compute_difference()

        if self.delta.ndim == 1:
            stat, p_val = stats.wilcoxon(self.delta)
            significant, conclusion = self._interpret_pvalue(p_val, alpha)

            return {
                "test": "Wilcoxon signed-rank",
                "stat": stat,
                "p_value": p_val,
                "alpha": alpha,
                "significant": significant,
                "conclusion": conclusion
            }

        else:
            results = {}
            for i, label in enumerate(self.labels):
                stat, p_val = stats.wilcoxon(self.delta[:, i])
                significant, conclusion = self._interpret_pvalue(p_val, alpha)

                results[label] = {
                    "test": "Wilcoxon signed-rank",
                    "stat": stat,
                    "p_value": p_val,
                    "alpha": alpha,
                    "significant": significant,
                    "conclusion": conclusion
                }
            return results


    #Kolmogorov-Smirnov test
    def ks_test(self, alpha=0.05):
        if self.genOur.ndim == 1:
            stat, p_val = stats.ks_2samp(self.genOur, self.genPythia)
            significant, conclusion = self._interpret_pvalue(p_val, alpha)

            return {
                "test": "Kolmogorov–Smirnov",
                "stat": stat,
                "p_value": p_val,
                "alpha": alpha,
                "significant": significant,
                "conclusion": conclusion
            }

        else:
            results = {}
            for i, label in enumerate(self.labels):
                stat, p_val = stats.ks_2samp(
                    self.genOur[:, i], self.genPythia[:, i]
                )
                significant, conclusion = self._interpret_pvalue(p_val, alpha)

                results[label] = {
                    "test": "Kolmogorov–Smirnov",
                    "stat": stat,
                    "p_value": p_val,
                    "alpha": alpha,
                    "significant": significant,
                    "conclusion": conclusion
                }
            return results"""
        
    def _interpret_significance(self, p_val):
        sigma = self._pvalue_to_sigma(p_val)

        if sigma >= 5:
            level = "5σ (YES)"
            significant = True
        elif sigma >= 3:
            level = "3σ (REJECT)"
            significant = True
        elif sigma >= 2:
            level = "2σ (REJECT)"
            significant = False
        else:
            level = "< 2σ (REJECT"
            significant = False

        return sigma, level, significant
    
    def print_result(self, result, label=None):
        name = result["test"]
        if label is not None:
            name += f" ({label})"

        print("=" * 50)
        print(name)
        print("-" * 50)
        print(f"p-value     : {result['p_value']:.3e}")
        print(f"significance: {result['sigma']:.2f} σ")
        print(f"interpretation: {result['level']}")

        if result["significant"]:
            print("→ Null hypothesis rejected")
        else:
            print("→ Null hypothesis not rejected")



    #Plot distributions
    def plot_distributions(self):
        if self.genOur.ndim == 1:
            sns.histplot(self.genOur, color='blue', label='Our Generator', kde=True)
            sns.histplot(self.genPythia, color='red', label='Pythia Generator', kde=True)
            plt.legend()
            plt.show()
        else:
            for i, label in enumerate(self.labels):
                plt.figure()
                sns.histplot(self.genOur[:, i], color='blue', label='Gen1', kde=True)
                sns.histplot(self.genPythia[:, i], color='red', label='Gen2', kde=True)
                plt.title(label)
                plt.legend()
                plt.show()

"""print(comp.paired_t_test())
print(comp.wilcoxon_test())
print(comp.ks_test())
comp.plot_distributions()

# Multi-dimensional example (3 observables per event)
gen1 = np.random.normal(10, 2, (1000, 3))
gen2 = np.random.normal(10.5, 2, (1000, 3))
labels = ["pT", "eta", "phi"]

comp = SimulatorComparison(gen1, gen2, labels)
print(comp.paired_t_test())
print(comp.wilcoxon_test())
print(comp.ks_test())
comp.plot_distributions()"""

