from google.cloud import storage
from google.cloud import bigquery
import numpy as np
import io
import pandas as pd
import pyarrow

storage_client = storage.Client()
bigquery_client = bigquery.Client()


def trigger(event, context):
    """Triggered by a change to a Cloud Storage bucket.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """

    data = read_data(event)

    # Extract columns
    x = np.array(data[:, 0])
    y = np.array(data[:, 1])

    """#### Defining the hyperparamters"""

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

    write_data(df, "lizzie-sandbox-310723.gdi_demo.cf_demo")


def read_data(event):
    bucket = storage_client.get_bucket(event['bucket'])
    blob = bucket.get_blob(event['name'])
    blob = blob.download_as_string()
    blob = blob.decode('utf-8')
    blob = io.StringIO(blob)
    data = np.genfromtxt(blob, delimiter=',')
    return data


def write_data(df, table_id):
    job_config = bigquery.LoadJobConfig(autodetect=True,
                                        write_disposition="WRITE_TRUNCATE",
                                        )
    job = bigquery_client.load_table_from_dataframe(df, table_id, job_config)
    job.result()


def compute_cost(b, m, data):
    total_cost = 0

    # number of data-points in training data
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

# if __name__ == "__main__":
#     trigger(event="", context="")
