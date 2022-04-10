import csv

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import numpy as np
import math

import base64, io

from quantum_ncs.classifier import QuantumNearestCentroid
from sklearn import datasets
from sklearn.metrics import accuracy_score
from sklearn.neighbors import NearestCentroid

from io import BytesIO

def get_graph():
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    graph = base64.b64encode(image_png)
    graph = graph.decode('utf-8')
    buffer.close()

    return graph

c_model = NearestCentroid()
q_model = QuantumNearestCentroid(error_rate=0.05)

def experiment (model, input_data):
    original_att_length = math.log2(input_data['data'].shape[1])
    floor_att_length = math.floor(original_att_length)
    if original_att_length.is_integer() :
        pass
    else : 

        input_data['data']= input_data['data'][:,:int(math.pow(2,floor_att_length))]

    X =  input_data['data']

    y = y_true = input_data['target']

    model.fit(X, y)

    y_pred = model.predict(X)
    score = accuracy_score(y_true, y_pred)
    error = 100 * (1. - score)

    return error


def plot_errors(c_error, q_errors, repetitions):
    labels = [str (repetition) for repetition in repetitions]

    x = np.arange(len(labels))
    width = 0.35

    plt.switch_backend('AGG')

    fig, ax = plt.subplots()
    ax.bar(x - width / 2, q_errors[0], width, label='w/o mitigation')
    ax.bar(x + width / 2, q_errors[1], width, label='mitigation')
    plt.axhline(y=c_error, color='black', linestyle='--', label='classical')

    ax.set_ylabel('Classification error %')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend(loc='lower right')

    fig.tight_layout()

    flike = io.BytesIO()
    fig.savefig(flike)
    chart = base64.b64encode(flike.getvalue()).decode()
    
    return chart


def train_and_test(input_data, repetitions = [10,50,100]):
    c_model = NearestCentroid()
    q_model = QuantumNearestCentroid(error_rate=0.05)
    c_error = experiment (c_model,input_data)
    q_errors = []
    
    for mitigation in [False, True]:
        errors = []
        q_model.error_mitigation = mitigation

        for repetition in repetitions:
            print(repetition)
            q_model.repetitions = repetition
            errors.append(experiment(q_model,input_data))

        q_errors.append(errors)

    chart = plot_errors(c_error, q_errors, repetitions)

    return chart


def read_file(csv_file):
    temp_data = {'data' : [],
                'target' : []}
    data ={'data' : [],
                'target' : []}
    # with open(path, mode='r') as csv_file:
    file_data = csv_file.read().decode("utf-8")
    lines = file_data.split("\n")

    csv_reader = csv.reader(lines)
    line_count = 0
    for row in csv_reader:
        if len(row)!= 0:
            temp_data['data'].append(row[:-1])
            temp_data['target'].append(row[-1])

    data['data'] = np.array(temp_data['data'],dtype=float)
    data['target'] = np.array(temp_data['target'])
    return data
