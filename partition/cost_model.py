import numpy as np
from scipy.optimize import minimize

## when v/e > threshold
x1 = np.array([0.58,5.75,0.58,0.91,3.58,1.38,1.16,1.28,1.21,0.96,1.01,0.85,0.44,0.58,3.16,0.38,0.41,0.46,0.51]) ## indicate v/e
x2 = np.array([8.905,118.657,5.109,7.671,32.812,2.319,1.944,2.155,2.027,1.610,1.692,1.422,0.742,0.976,5.315,0.378,0.394,0.424,0.465]) ## edge mem number / 1M
y = np.array([0.394,0.049,0.648,0.472,0.153,0.253,0.289,0.268,0.284,0.340,0.328,0.372,0.563,0.483,0.123,0.720,0.720,0.691,0.640]) ## MTEPS / 1200

# Define the function to be fitted
def func_to_optimize(params, x1, x2, y):
    a, b, c = params
    y_pred = 1 / (a*x1 + b*x2 + c)
    return np.mean((y_pred - y)**2)  # Loss: mean squared error

# Initial guesses for a, b, c
initial_params = [0.1, 0.1, 0.1]

# Minimize the error
res = minimize(func_to_optimize, initial_params, args=(x1, x2, y), method='L-BFGS-B')

# Extract optimized parameters
a_opt, b_opt, c_opt = res.x
print("Optimized parameters:", a_opt, b_opt, c_opt)

def predict(x1, x2, a, b, c):
    return 1 / (a*x1 + b*x2 + c)

x1_pred = [1.15,1.11,0.92,1.02,0.71,0.57,0.55,0.51,0.38,0.12,0.04]
x2_pred = [1.930,1.858,1.543,1.707,1.189,0.668,0.596,0.532,0.383,0.179,8.689]

for idx in range(len(x1_pred)):
    y_pred = predict(x1_pred[idx], x2_pred[idx], a_opt, b_opt, c_opt)
    print (y_pred)


## when v/e <= threshold
x1 = np.array([8.689,0.830,2.213,4.634,0.422]) ## indicate v/e
y = np.array([0.633,0.985,0.885,0.698,1.070]) ## MTEPS / 1200

# Define the function to be fitted
def func_2(params, x1, y):
    a, b = params
    y_pred = 1 / (a*x1 + b)
    return np.mean((y_pred - y)**2)  # Loss: mean squared error

# Initial guesses for a, b, c
initial_params = [0.1, 0.1]

# Minimize the error
res = minimize(func_2, initial_params, args=(x1, y), method='L-BFGS-B')

# Extract optimized parameters
a_opt, b_opt = res.x
print("Function 2 Optimized parameters:", a_opt, b_opt)


