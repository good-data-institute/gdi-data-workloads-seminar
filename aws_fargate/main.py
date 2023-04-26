import os
import numpy as np
import io
import pandas as pd
import pyarrow
import urllib.request
import boto3
from flask import Flask

app = Flask(__name__)

s3 = boto3.client('s3')


@app.route("/")
def trigger():

    urllib.request.urlretrieve(
        "https://raw.githubusercontent.com/CC-MNNIT/2018-19-Classes/master/MachineLearning/2018_08_22_Logical-Rhythm-2/data.csv",
        "data.csv")
    data = np.genfromtxt('data.csv', delimiter=',')

    # Extract columns
    x = np.array(data[:, 0])
    y = np.array(data[:, 1])

    """#### Defining the hyper-parameters"""

    # hyper-parameters
    learning_rate = 0.0001
    initial_b = 0
    initial_m = 0
    num_iterations = 10

    """#### Run gradient_descent() to get optimized parameters b and m"""

    b, m, cost_graph, b_progress, m_progress = gradient_descent(data, initial_b, initial_m, learning_rate,
                                                                num_iterations)

    # Predict y values
    p = m * x + b

    # output data
    df = pd.DataFrame({'study_hours': x, 'test_score': list(y), 'pr_test_score': list(p)},
                      columns=['study_hours', 'test_score', 'pr_test_score'])

    write_data(df, 's3://gdi-seminar/fargate/output_data')

    return 'success'


def write_data(df, s3_path):
    # csv_buffer = io.StringIO()
    # df.to_csv(csv_buffer)
    # s3.put_object(Body=csv_buffer.getvalue(), Bucket=bucket_name, Key=object_key)

    out_buffer = io.BytesIO()
    df.to_parquet(out_buffer, index=False)

    s3.put_object(Body=out_buffer.getvalue(), Bucket=s3_path.split('/')[2], Key='/'.join(s3_path.split('/')[3:]))


def compute_cost(b, m, data):
    total_cost = 0

    # number of datapoints in training data
    N = float(len(data))

    # Compute sum of squared errors
    for i in range(0, len(data)):
        x = data[i, 0]
        y = data[i, 1]
        total_cost += (y - (m * x + b)) ** 2

    # Return average of squared error
    return total_cost / (2 * N)


def step_gradient(b_current, m_current, data, alpha):
    """takes one step down towards the minima

    Args:
        b_current (float): current value of b
        m_current (float): current value of m
        data (np.array): array containing the training data (x,y)
        alpha (float): learning rate / step size

    Returns:
        tuple: (b,m) new values of b,m
    """

    m_gradient = 0
    b_gradient = 0
    N = float(len(data))

    # Calculate Gradient
    for i in range(0, len(data)):
        x = data[i, 0]
        y = data[i, 1]
        m_gradient += - (2 / N) * x * (y - (m_current * x + b_current))
        b_gradient += - (2 / N) * (y - (m_current * x + b_current))

    # Update current m and b
    m_updated = m_current - alpha * m_gradient
    b_updated = b_current - alpha * b_gradient

    # Return updated parameters
    return b_updated, m_updated


def gradient_descent(data, starting_b, starting_m, learning_rate, num_iterations):
    """runs gradient descent

    Args:
        data (np.array): training data, containing x,y
        starting_b (float): initial value of b (random)
        starting_m (float): initial value of m (random)
        learning_rate (float): hyperparameter to adjust the step size during descent
        num_iterations (int): hyperparameter, decides the number of iterations for which gradient descent would run

    Returns:
        list : the first and second item are b, m respectively at which the best fit curve is obtained, the third and fourth items are two lists, which store the value of b,m as gradient descent proceeded.
    """

    # initial values
    b = starting_b
    m = starting_m

    # to store the cost after each iteration
    cost_graph = []

    # to store the value of b -> bias unit, m-> slope of line after each iteration (pred = m*x + b)
    b_progress = []
    m_progress = []

    # For every iteration, optimize b, m and compute its cost
    for i in range(num_iterations):
        cost_graph.append(compute_cost(b, m, data))
        b, m = step_gradient(b, m, np.array(data), learning_rate)
        b_progress.append(b)
        m_progress.append(m)

    return [b, m, cost_graph, b_progress, m_progress]


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

