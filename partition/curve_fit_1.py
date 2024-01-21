import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

# MTEPS = a / (b * x1 + (c / x2) + d) + e
# new: MTEPS = -7809 / (-2.8505 * v_e_ratio[p_idx] + (-2480 / edge_op[p_idx]) -3.0395) -1012

def fit_function(x, a, b, c, d, e):
    x1, x2 = x
    return a / (b * x1 + (c / x2) + d) + e

def GetMteps(x):
    x1, x2 = x
    MTEPS = -7809 / (-2.8505 * x1 + (-2480 / x2) -3.0395) -1012
    MTEPS[MTEPS < 0] = 8
    return MTEPS

v_e_ratio_1 = np.loadtxt("./m_access/G25_v_e_ratio.txt")
edge_op_1 = np.loadtxt("./m_access/G25_e_op.txt")
MTEPS_1 = np.loadtxt("./m_access/G25_MTEPS.txt")

v_e_ratio_2 = np.loadtxt("./m_access/TW_v_e_ratio.txt")
edge_op_2 = np.loadtxt("./m_access/TW_e_op.txt")
MTEPS_2 = np.loadtxt("./m_access/TW_MTEPS.txt")

v_e_ratio = np.hstack([v_e_ratio_1, v_e_ratio_2])
edge_op = np.hstack([edge_op_1, edge_op_2])
MTEPS = np.hstack([MTEPS_1, MTEPS_2])

print (v_e_ratio)
print (edge_op)
print (MTEPS)


x_data = np.vstack([v_e_ratio, edge_op])
params, covariance = curve_fit(fit_function, x_data, MTEPS)

a, b, c, d, e = params
print (a, b, c, d, e)


in_data = np.vstack([v_e_ratio, edge_op])
MTEPS_fit = fit_function(in_data, a, b, c, d, e)
print (MTEPS_fit)
print (MTEPS - MTEPS_fit)

v_e_ratio = np.loadtxt("./m_access/Friendster_v_e_ratio.txt")
edge_op = np.loadtxt("./m_access/Friendster_e_op.txt")

MTEPS_real = GetMteps(np.vstack([v_e_ratio, edge_op]))

MTEPS_2 = -225581 / (1624 * v_e_ratio + (-7022029888 / edge_op) -125) -7.54
MTEPS_2[MTEPS_2 < 0] = 8

# plt.scatter(v_e_ratio, MTEPS_real)
# plt.scatter(v_e_ratio, MTEPS_2)

print (MTEPS_real - MTEPS_2)
plt.scatter(v_e_ratio, (MTEPS_real - MTEPS_2))
plt.xlabel('x1')
plt.ylabel('y')
plt.title('Scatter Plot of x1 vs y')
plt.grid(True)
plt.savefig('./scatter_plot_MTEPS_1.png')
plt.close()