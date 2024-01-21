import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

def fit_function(x, a, b):
    return np.minimum(1.4, a / (b * x + 0.488))

# Sample data (replace these with your actual data)

v_e = np.loadtxt("unified_v_e.txt")
MTEPS = np.loadtxt("unified_MTEPS.txt")/1000

mask = v_e <= 2.5
v_e_filtered = v_e[mask]
MTEPS_filtered = MTEPS[mask]

# Find the maximum y value for each unique x value
unique_x = np.unique(v_e_filtered)
fitted_y_max = np.minimum(1.4, 1 / (1.23 * unique_x + 0.488))
fitted_y_min = np.minimum(1.4, 0.42 / (1.23 * unique_x + 0.488))

# Plotting
plt.figure(figsize=(6,3))
plt.plot(unique_x, fitted_y_max, label='Upper-bound curve', color='red', linestyle='--', linewidth=2)
plt.plot(unique_x, fitted_y_min, label='Lower-bound curve', color='blue', linestyle='--', linewidth=2)
plt.scatter(v_e_filtered, MTEPS_filtered, label='Subgraphs', color='black', marker='x', s=30)

# Setting labels for axes with bold font
plt.xlabel('X-axis', fontweight='bold')
plt.ylabel('Y-axis', fontweight='bold')

# Adding the legend with bold font
legend = plt.legend(fontsize='large')
for text in legend.get_texts():
    text.set_fontweight('bold')
    
    
    
plt.legend()
plt.savefig('unified_model.png')

