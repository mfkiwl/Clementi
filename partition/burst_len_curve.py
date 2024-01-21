import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

Max_MTEPS = 1171
scale = Max_MTEPS

def inverse_proportion(x, a, b, c):
    return a / (x + b) + c

## curve fit for differnet burst length
## burst_length = 64

x_burst_64 = np.array([0.375,0.4,0.425,0.725,1.025,1.6])
y_burst_64 = np.array([1082,950,845,432,395,335]) / scale

params, covariance = curve_fit(inverse_proportion, x_burst_64, y_burst_64)
a_burst_64, b_burst_64, c_burst_64 = params

## burst_length = 32
x_burst_32 = np.array([0.3,0.325,0.375,0.425,0.725,1.7])
y_burst_32 = np.array([1069,935,772,614,390,262]) / scale

params, covariance = curve_fit(inverse_proportion, x_burst_32, y_burst_32)
a_burst_32, b_burst_32, c_burst_32 = params


## burst_length = 16
x_burst_16 = np.array([0.225,0.25,0.275,0.375,0.4,0.725,1.025,1.725])
y_burst_16 = np.array([1044,977,841,557,547,366,289,193]) / scale

params, covariance = curve_fit(inverse_proportion, x_burst_16, y_burst_16)
a_burst_16, b_burst_16, c_burst_16 = params

## burst_length = 8
x_burst_8 = np.array([0.15,0.175,0.2,0.225,0.725,1.025,1.6])
y_burst_8 = np.array([1085,958,825,797,285,203,129]) / scale

params, covariance = curve_fit(inverse_proportion, x_burst_8, y_burst_8)
a_burst_8, b_burst_8, c_burst_8 = params

## burst_length = 4
x_burst_4 = np.array([0.075,0.1,0.125,0.175,0.3,0.425,0.725,1.025,1.6])
y_burst_4 = np.array([1095,896,730,594,366,263,155,110,72]) / scale

params, covariance = curve_fit(inverse_proportion, x_burst_4, y_burst_4)
a_burst_4, b_burst_4, c_burst_4 = params

## burst_length = 2
x_burst_2 = np.array([0.025,0.05,0.075,0.15,0.725,1.025,1.55, 1.75])
y_burst_2 = np.array([1175,896,673,368,81,58,38,34]) / scale

params, covariance = curve_fit(inverse_proportion, x_burst_2, y_burst_2)
a_burst_2, b_burst_2, c_burst_2 = params

## burst_length = 1
x_burst_1 = np.array([0.15,0.175,0.2,0.225,0.35,0.375,0.4,0.725,1.575])
y_burst_1 = np.array([1035,950,841,740,543,515,480,283,136]) / scale

params, covariance = curve_fit(inverse_proportion, x_burst_1, y_burst_1)
a_burst_1, b_burst_1, c_burst_1 = params

## The MTEPS curve contains a static value and a inverse_proportion
x_fit = np.linspace(0, 2.5, 100) ## set x range [0, 5]
y_fit_64 = inverse_proportion(x_fit, a_burst_64, b_burst_64, c_burst_64) 
y_fit_32 = inverse_proportion(x_fit, a_burst_32, b_burst_32, c_burst_32) 
y_fit_16 = inverse_proportion(x_fit, a_burst_16, b_burst_16, c_burst_16) 
y_fit_8 = inverse_proportion(x_fit, a_burst_8, b_burst_8, c_burst_8) 
y_fit_4 = inverse_proportion(x_fit, a_burst_4, b_burst_4, c_burst_4) 
y_fit_2 = inverse_proportion(x_fit, a_burst_2, b_burst_2, c_burst_2) 
y_fit_1 = inverse_proportion(x_fit, a_burst_1, b_burst_1, c_burst_1) 
for y in range(len(x_fit)):
    if (y_fit_64[y] > 1):
        y_fit_64[y] = 1
    elif (y_fit_64[y] < 0):
        y_fit_64[y] = 1
    
    if (y_fit_32[y] > 1):
        y_fit_32[y] = 1
    elif (y_fit_32[y] < 0):
        y_fit_32[y] = 1

    if (y_fit_16[y] > 1):
        y_fit_16[y] = 1
    elif (y_fit_16[y] < 0):
        y_fit_16[y] = 1

    if (y_fit_8[y] > 1):
        y_fit_8[y] = 1
    elif (y_fit_8[y] < 0):
        y_fit_8[y] = 1

    if (y_fit_4[y] > 1):
        y_fit_4[y] = 1
    elif (y_fit_4[y] < 0):
        y_fit_4[y] = 1

    if (y_fit_2[y] > 1):
        y_fit_2[y] = 1
    elif (y_fit_2[y] < 0):
        y_fit_2[y] = 1

    if (y_fit_1[y] > 1):
        y_fit_1[y] = 1
    elif (y_fit_1[y] < 0):
        y_fit_1[y] = 1

## plt.scatter(x_data, y_data * scale, label='Original Data')
plt.plot(x_fit, y_fit_64, label='burst_len = 64', color='red')
plt.scatter(x_burst_64, y_burst_64, color='red', marker="D", s=10)
x_extend_64 = np.array([0.05, 0.225])
y_extend_64 = np.array([1.0 , 1.0])
plt.scatter(x_extend_64, y_extend_64, color='red', marker="D", s=10)

plt.plot(x_fit, y_fit_32, label='burst_len = 32', color='orange')
plt.scatter(x_burst_32, y_burst_32, color='orange', marker="D", s=10)
x_extend_32 = np.array([0.075, 0.2])
y_extend_32 = np.array([1.0 , 1.0])
plt.scatter(x_extend_32, y_extend_32, color='orange', marker="D", s=10)

plt.plot(x_fit, y_fit_16, label='burst_len = 16', color='blue')
plt.scatter(x_burst_16, y_burst_16, color='blue', marker="D", s=10)
x_extend_16 = np.array([0.15])
y_extend_16 = np.array([1.0])
plt.scatter(x_extend_16, y_extend_16, color='blue', marker="D", s=10)

plt.plot(x_fit, y_fit_8, label='burst_len = 8', color='black')
plt.scatter(x_burst_8, y_burst_8, color='black', marker="D", s=10)

plt.plot(x_fit, y_fit_4, label='burst_len = 4', color='brown')
plt.scatter(x_burst_4, y_burst_4, color='brown', marker="D", s=10)

plt.plot(x_fit, y_fit_2, label='burst_len = 2', color='purple')
plt.scatter(x_burst_2, y_burst_2, color='purple', marker="D", s=10)

plt.plot(x_fit, y_fit_1, label='burst_len = 1', color='darkorange')
plt.scatter(x_burst_1, y_burst_1, color='darkorange', marker="D", s=10)


plt.ylim(0, 1.2)
plt.xlabel('v/e data volume ratio')
plt.ylabel('Normalized MTEPS')
plt.legend()
plt.title('Graph processing performance using different burst length')

plt.savefig('MTEPS_burst_length.png', dpi=300)