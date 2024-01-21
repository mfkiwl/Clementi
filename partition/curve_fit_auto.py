import argparse
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures

global mode
global print_enable
mode=2
print_enable=True

def fit_and_predict_3(x1, x2, y):
    """
    Fit a linear model y = a*x1^2 + b*x1 + c*x2 + d and predict values for each (x1, x2).
    :param x1: numpy array of values for x1.
    :param x2: numpy array of values for x2.
    :param y: numpy array of values for y.
    :return: model coefficients and intercept.
    """
    # Combine x1 and x2 into a single feature matrix
    X = np.column_stack((x1, x2))

    # Generate polynomial features for x1 (x1 and x1^2)
    poly = PolynomialFeatures(degree=2, include_bias=False)
    X_poly = poly.fit_transform(X[:, 0].reshape(-1, 1))
    
    # Combine x1, x1^2, and x2 into the final feature matrix
    X_final = np.column_stack((X_poly, X[:, 1]))

    # Fit the linear regression model
    model = LinearRegression().fit(X_final, y)

    # Predict y values using the fitted model
    y_pred = model.predict(X_final)

    # Print details in the specified format
    if print_enable == True:
        for i in range(len(y)):
            print(f"Partition = {i+1}, x1 = {int(x1[i])}, x2 = {int(x2[i])}, y_predict = {int(y_pred[i])}, y = {int(y[i])}, error = {abs(y[i] - y_pred[i])/ y[i] :.4f}%")

    return model.coef_, model.intercept_


def fit_and_predict_2(x1, x2, y):
    """
    Fit a linear model y = a*x1 + b*x2 + c and predict values for each (x1, x2).
    :param x1: numpy array of values for x1.
    :param x2: numpy array of values for x2.
    :param y: numpy array of values for y.
    :return: coefficients a, b and intercept c.
    """
    # Combine x1 and x2 into a single feature matrix
    X = np.column_stack((x1, x2))

    # Fit the linear regression model
    model = LinearRegression().fit(X, y)

    # Predict y values using the fitted model
    y_pred = model.predict(X)

    # Print details in the specified format
    if print_enable == True:
        for i in range(len(y)):
            print(f"Partition = {i+1}, x1 = {int(x1[i])}, x2 = {int(x2[i])}, y_predict = {int(y_pred[i])}, y = {int(y[i])}, error = {abs(y[i] - y_pred[i])/ y[i] :.4f}%")

    return model.coef_[0], model.coef_[1], model.intercept_



def fit_and_predict(x1, x2, y):
    """
    Fit a linear model y = a*x1 + b*x2 and predict values for each (x1, x2).
    :param x1: numpy array of values for x1.
    :param x2: numpy array of values for x2.
    :param y: numpy array of values for y.
    :return: coefficients a and b.
    """
    # Combine x1 and x2 into a single feature matrix
    X = np.column_stack((x1, x2))

    # Fit the linear regression model
    model = LinearRegression().fit(X, y)

    # Predict y values using the fitted model
    y_pred = model.predict(X)

    # Print details in the specified format
    if print_enable == True:
        for i in range(len(y)):
            print(f"Partition = {i+1}, x1 = {int(x1[i])}, x2 = {int(x2[i])}, y_predict = {int(y_pred[i])}, y = {int(y[i])}, error = {abs(y[i] - y_pred[i])/ y[i] :.4f}%")

    return model.coef_[0], model.coef_[1]

# Example usage
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Fit a linear model y = a*x1 + b*x2 to the given dataset.')
    parser.add_argument('dataset_name', type=str, help='The name of the dataset to process.')

    args = parser.parse_args()

    vertex_op = np.loadtxt("./m_access/" + args.dataset_name + "_v_op.txt")
    edge_op = np.loadtxt("./m_access/" + args.dataset_name + "_e_op.txt")
    MTEPS = np.loadtxt("./m_access/" + args.dataset_name + "_MTEPS.txt")

    # Load your dataset here
    if print_enable == True:
        print("Fitting Dataset: " + args.dataset_name)
    # For demonstration, I'll create dummy data
    x1 = vertex_op
    x2 = edge_op
    y = edge_op/MTEPS *256 ## each e_op should be 256 edges

    # Fit the model and predict
    if (mode == 1):
        a, b = fit_and_predict(x1, x2, y)
        print("Dataset: " + args.dataset_name  + f" Fitted model: Time = {a:.2f}*V_op + {b:.2f}*E_op")
    elif (mode == 2):
        a, b, c = fit_and_predict_2(x1, x2, y)
        print("Dataset: " + args.dataset_name  + f" Fitted model: Time = {a:.2f}*V_op + {b:.2f}*E_op + {c:.2f}")
    elif (mode == 3):
        coefficients, intercept = fit_and_predict_3(x1, x2, y)
        print("Dataset: " + args.dataset_name  + f" Fitted model: Time = {coefficients[0]:.2f}*V_op^2 + {coefficients[1]:.2f}*V_op + {coefficients[2]:.2f}*E_op + {intercept:.2f}")
