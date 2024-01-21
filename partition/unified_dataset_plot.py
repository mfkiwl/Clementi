import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

def fit_function(x, a, b):
    return np.minimum(1.4, a / (b * x + 0.488))

# Sample data (replace these with your actual data)

dataset = ['G25', "UK2007-05", "Friendster"]
plt.figure(figsize=(6,3))

colors = ['green', 'brown', 'purple']  # Different colors for each dataset
markers = ['^', '+', '*', 'd']  # Different markers for each dataset
linestyles = ['--', '-.', ':', '-']  # Different line styles for each dataset

x_range = np.linspace(0, 1.5, 100)

for i, data in enumerate(dataset):
    print (data)
    
    v_e = np.loadtxt("./m_access/" + data + "_v_e_ratio.txt")
    MTEPS = np.loadtxt("./m_access/" + data + "_MTEPS.txt")/1000

    mask = v_e <= 1.5
    v_e_filtered = v_e[mask]
    MTEPS_filtered = MTEPS[mask]

    params, params_covariance = curve_fit(fit_function, v_e_filtered, MTEPS_filtered, p0=[1, 1])
    fitted_y = fit_function(x_range, params[0], params[1])

    # Plotting
    if data == 'UK2007-05':
        data = 'UK'
    if data == 'Friendster':
        data = 'FR'
    plt.plot(x_range, fitted_y, label=data + ' fitted curve', color=colors[i], linestyle=linestyles[i], linewidth=2)
    plt.scatter(v_e_filtered, MTEPS_filtered, label=data + ' subgraphs', color=colors[i], marker=markers[i], s=30)
    # plt.xlabel('V/E', fontsize = 16)
    # plt.ylabel('GTEPS', fontsize = 16)
    # plt.legend()
plt.legend()
plt.savefig('unified_dataset.png')

