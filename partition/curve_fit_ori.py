import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

scale = 1000
Max_MTEPS = 1290

plt.figure(figsize=(8,5))

def inverse_proportion(x, a, b, c):
    return a / (x + b) + c

## MTEPS vs V/E volume
x_data = np.array([0.35,0.375,0.4,0.425,0.825,0.9,1.075,1.125,1.125,2.225,2.35])
y_data = np.array([1271,1188,1030,905,432,429,399,383,383,298,283]) / scale

params, covariance = curve_fit(inverse_proportion, x_data, y_data)

a_fit, b_fit, c_fit = params

## The MTEPS curve contains a static value and a inverse_proportion
x_fit = np.linspace(0, 4, 100) ## set x range [0, 5]
y_fit = inverse_proportion(x_fit, a_fit, b_fit, c_fit) * scale
for y in range(len(y_fit)):
    if (y_fit[y] > Max_MTEPS):
        y_fit[y] = Max_MTEPS
    elif (y_fit[y] < 0):
        y_fit[y] = Max_MTEPS

## add real and systhesis graph dataset
x_TW = np.array([1.161,0.121,0.001,0.015,0.019,0.002,0.001,0.000,0.001,0.003,0.023,0.081,0.035,0.080,0.555,0.423]) 
y_TW = np.array([363,1014,1228,1184,1148,1217,1228,1237,1220,1230,1190,1132,1193,1147,577,707])
plt.scatter(x_TW, y_TW, label='TW', color='red', marker="o")

x_FR = np.array([0.622,0.290,0.265,0.272,0.276,0.217,0.189,0.178,0.166,0.203,0.287,0.306,0.318,0.450,0.908,3.654]) 
y_FR = np.array([600,1022,1092,1066,1050,1176,1192,1189,1182,1158,1036,986,952,699,408,134])
plt.scatter(x_FR, y_FR, label='Friendster', color='blue', marker="^")

x_UK = np.array([0.185,0.006,0.007,0.015,0.005,0.001,0.001,0.010,0.029,0.024,0.360,0.765,0.536,0.292,0.160,0.546])
y_UK = np.array([874,1134,1106,1085,1131,1159,1159,1085,967,952,507,336,418,581,647,409])
plt.scatter(x_UK, y_UK, label='UK2007-05', color='green', marker="x")

x_G25 = np.array([0.051,0.083,0.109,0.030,0.069,0.105,0.058,0.109,0.097,0.144,0.041,0.054,0.054,0.080,0.023,0.069])
y_G25 = np.array([1104,1128,1141,1123,1113,1106,1118,1093,1110,1071,1115,1129,1135,1116,1127,1128])
plt.scatter(x_G25, y_G25, label='G25', color='black', marker="*")

## plt.scatter(x_data, y_data * scale, label='Original Data')
plt.plot(x_fit, y_fit, label='Edge/Vertex Bound', color='orange')
plt.ylim(0, 1400)
plt.xlabel('M_v/M_e', fontsize=16, fontweight='bold')
plt.ylabel('MTEPS', fontsize=16, fontweight='bold', labelpad=1)
plt.legend(prop={'size': 16, 'weight': 'bold'})
plt.title('Performance for subgraphs', fontsize=20, fontweight='bold')
# Adjust tick font size
ax = plt.gca()
for label in ax.get_xticklabels():
    label.set_fontsize(12)
    label.set_fontweight('bold')
for label in ax.get_yticklabels():
    label.set_fontsize(12)
    label.set_fontweight('bold')
    
# plt.text(0.46, -0.14, "(b)", fontsize=18, fontweight='bold', transform=ax.transAxes)

plt.savefig('original_partition.png', dpi=300)
plt.savefig('original_partition.pdf', dpi=300)