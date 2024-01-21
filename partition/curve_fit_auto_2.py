import argparse
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize

def segmented_function(params, x):
    a, b, c = params
    return np.minimum(1.4, a / (b * x + 0.488))

def objective_function(params, x, y, e_op):
    y_pred = segmented_function(params, x)
    y_pred[y_pred < 0.1] = 0.1
    weighted_error = e_op * np.sqrt((y - y_pred) ** 2) / y / y_pred
    return np.mean(weighted_error)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Fit a linear model y = a*x1 + b*x2 to the given dataset.')
    parser.add_argument('dataset_name', type=str, help='The name of the dataset to process.')

    args = parser.parse_args()

    v_e_op = np.loadtxt("./m_access/" + args.dataset_name + "_v_e_ratio.txt")
    e_op = np.loadtxt("./m_access/" + args.dataset_name + "_e_op.txt")
    MTEPS = np.loadtxt("./m_access/" + args.dataset_name + "_MTEPS.txt")

    x = v_e_op
    y = MTEPS / 1000  # GTEPS
    e_op_t = e_op / max(e_op)
    
    initial_params = [0.9, 2, 0.1]
    bounds = [(0, 1.0), (0.5, 7.8125), (-0.5, 0.5)]  # Bounds for a, b, and c

    result = minimize(objective_function, initial_params, args=(x, y, e_op_t), bounds=bounds, method='L-BFGS-B')

    if result.success:
        y_fit = segmented_function(result.x, x)

        abs_error_sum = np.sum(np.abs(e_op/y_fit - e_op/y))
        error_percentage = (abs_error_sum / np.sum(e_op/y)) * 100

        total_time = 0
        print ("MTEPS_input = ", y*1000)
        print ("MTEPS_pred = ", y_fit*1000)

        for i in range(len(e_op)):
            print ("Partition id = ", i+1, " execution time error ratio = ", abs(e_op[i]/y_fit[i] - e_op[i]/y[i])/(e_op[i]/y[i])*100, "%")
            partial_time = e_op[i]/y_fit[i]/1000*8/4  ## 1000 MTEPS = 1 GTEPS, 8 edge per operation and 4 PEs in a FPGA;
            total_time += partial_time
            # print (partial_time/1000, " ms")
        
        overhead = 2000 ## us, each partition switching and system call(start + end) + pipeline initialization
        total_time += len(e_op) * overhead ## PCIe switching
        print (total_time/1000, " ms")

        
        plt.figure(figsize=(10, 6))
        plt.scatter(x, y, label='Original Data (y, x)', alpha=0.6)
        plt.scatter(x, y_fit, label='Fitted Data (y_fit, x)', alpha=0.6)
        plt.xlabel('x')
        plt.ylabel('y')
        plt.title('Comparison of Original and Fitted Data')
        plt.legend()
        plt.savefig('fitted_data_comparison.png')

        
        a, b, c = result.x
        print(f" GTEPS = min(1.4, {a:.3f} / ({b:.3f} * (M_v/M_e) + 0.488)), error ratio = {error_percentage:.3f} %")
    else:
        print("Optimization failed:", result.message)