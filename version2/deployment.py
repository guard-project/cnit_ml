import ast
import json
import time
from os import environ

import numpy as np
import pandas as pd
from joblib import load
from kafka import KafkaConsumer, KafkaProducer

scaler = load('scaler.joblib')
cols = load('columns.joblib')
class_names = load('class_names.joblib')
grid_clf_acc = load('rfmodel_multiclass.joblib')

kafka_bootstrap_servers = environ.get(
    'KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
kafka_topic = environ.get('KAFKA_TOPIC', 'network-data')

producer = KafkaProducer(bootstrap_servers=kafka_bootstrap_servers)
consumer = KafkaConsumer(
    kafka_topic, bootstrap_servers=kafka_bootstrap_servers)

rep_time = 60
time_to_report = time.time() + rep_time
attackers = {}
for msg in consumer:

    message = msg.value.decode('utf-8')
    message2 = ast.literal_eval(message)

    testing = []
    for i in cols:
        testing.append(float(message2[i]))
    # test = pd.DataFrame([testing], columns = cols)
    test = pd.DataFrame(scaler.transform(
        np.asarray(testing).reshape(1, -1)), columns=cols)
    test_preds = grid_clf_acc.predict(test)
    print("FLOW ID:", message2['FLOW_ID'],
          "result: class", class_names[test_preds[0]])

    if test_preds[0] != 0:
        if message2["IPV4_SRC_ADDR"] not in attackers:
            attackers[message2["IPV4_SRC_ADDR"]] = {}
        if class_names[test_preds[0]] not in attackers[message2["IPV4_SRC_ADDR"]]:
            attackers[message2["IPV4_SRC_ADDR"]
                      ][class_names[test_preds[0]]] = 1
        else:
            attackers[message2["IPV4_SRC_ADDR"]][class_names[test_preds[0]]
                                                 ] = attackers[message2["IPV4_SRC_ADDR"]][class_names[test_preds[0]]] + 1

    if time.time() >= time_to_report:
        if attackers:
            output = {"SOURCE": "ALGO112_RF", "SEVERITY": "10",
                      "DESCRIPTION": "DDoS Attack(s)", "DATA": attackers, "TIMESTAMP": time.time()}
            producer.send('detection-results',
                          json.dumps(output).encode('utf-8'))
            print(attackers)
            attackers = {}
        time_to_report = time.time() + rep_time
