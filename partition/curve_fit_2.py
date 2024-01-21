import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

# MTEPS = 1500 / (0.879 * v_e_ratio[p_idx] + (4*1024*1024*0.0155 / edge_op[p_idx]) + 0.468)
# new: MTEPS = -13960861 / (-23750 * v_e_ratio[p_idx] + (4*1024*1024*0.0155 / edge_op[p_idx]) -7880) -12.057


def fit_function(x, a, b, c, d, e):
    x1, x2 = x
    return a / (b * x1 + (c/x2) + d) + e

def GetMteps(x):
    x1, x2 = x
    MTEPS = -13960861 / (-23750 * x1 + (4*1024*1024*0.0155 / x2) -7880) -12.057
    MTEPS[MTEPS < 0] = 8
    return MTEPS

v_e_ratio = np.loadtxt("./m_access/Friendster_v_e_ratio.txt")
edge_op = np.loadtxt("./m_access/Friendster_e_op.txt")
MTEPS = np.loadtxt("./m_access/Friendster_MTEPS.txt")

x_data = np.vstack([v_e_ratio, edge_op])
params, covariance = curve_fit(fit_function, x_data, MTEPS)

a, b, c, d, e = params
print (a, b, c, d, e)

in_data = np.vstack([v_e_ratio, edge_op])
MTEPS_fit = fit_function(in_data, a, b, c, d, e)
print (MTEPS_fit)
print (MTEPS - MTEPS_fit)

MTEPS_real = GetMteps(np.vstack([v_e_ratio, edge_op]))
plt.scatter(v_e_ratio, MTEPS_real)
plt.xlabel('x1')
plt.ylabel('y')
plt.title('Scatter Plot of x1 vs y')
plt.grid(True)
plt.savefig('./scatter_plot_MTEPS_2.png')
plt.close()