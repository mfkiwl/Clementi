import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

scale = 1000
Max_MTEPS = 1290

def inverse_proportion(x, a, b, c):
    return a / (x + b) + c

## MTEPS vs V/E volume
x_data = np.array([0.35,0.375,0.4,0.425,0.825,0.9,1.075,1.125,1.125,2.225,2.35])
y_data = np.array([1271,1188,1030,905,432,429,399,383,383,298,283]) / scale

params, covariance = curve_fit(inverse_proportion, x_data, y_data)

a_fit, b_fit, c_fit = params
print (params)

## The MTEPS curve contains a static value and a inverse_proportion
x_fit = np.linspace(0, 4, 100) ## set x range [0, 5]
y_fit = inverse_proportion(x_fit, a_fit, b_fit, c_fit) * scale
for y in range(len(y_fit)):
    if (y_fit[y] > Max_MTEPS):
        y_fit[y] = Max_MTEPS
    elif (y_fit[y] < 0):
        y_fit[y] = Max_MTEPS

## add real and systhesis graph dataset
x_TW = np.array([0.113,0.146,0.148,0.148,0.157,0.160,0.165,0.168,0.168,0.168,0.168,0.168,0.168,0.168,0.168,0.168]) 
y_TW = np.array([1005,922,914,917,896,894,874,952,944,947,952,953,951,955,953,948])
# plt.scatter(x_TW, y_TW, label='TW', color='red', marker="o")

x_FR = np.array([0.538,0.538,0.538,0.538,0.538,0.538,0.538,0.538,0.538,0.538,0.538,0.538,0.538,0.538,0.538,0.538]) 
y_FR = np.array([657,666,664,667,664,667,655,661,596,755,600,666,757,666,664,662])
# plt.scatter(x_FR, y_FR, label='Friendster', color='blue', marker="^")

x_UK = np.array([0.169,0.171,0.183,0.184,0.184,0.187,0.187,0.187,0.187,0.187,0.187,0.187,0.187,0.187,0.187,0.187])
y_UK = np.array([774,773,753,751,752,743,741,748,740,741,740,738,745,749,740,737])
# plt.scatter(x_UK, y_UK, label='UK2007-05', color='green', marker="x")

x_G25 = np.array([0.073,0.073,0.073,0.073,0.073,0.073,0.073,0.074,0.074,0.074,0.074,0.074,0.074,0.074,0.074,0.074])
y_G25 = np.array([1245,1253,1239,1243,1230,1229,1139,1096,1103,1125,1117,1085,1124,1109,1100,1111])
# plt.scatter(x_G25, y_G25, label='G25', color='black', marker="*")

## plt.scatter(x_data, y_data * scale, label='Original Data')
plt.plot(x_fit, y_fit, label='Performance Bound', color='orange')
plt.ylim(0, 1400)
plt.xlabel('v/e data volume ratio')
plt.ylabel('MTEPS')
plt.legend()
# plt.title('Graph processing performance under balanced partition method')
plt.title('Performance model curve')

# plt.savefig('balanced_partition.png', dpi=300)
plt.savefig('perf_model_curve.png', dpi=300)