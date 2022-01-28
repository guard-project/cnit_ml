import ast
import json
import os
import time

import numpy as np
import pandas as pd
from about import project, title, version  # noqa: E402
from dynaconf import Dynaconf
from joblib import load
from kafka import KafkaConsumer, KafkaProducer
from rich.console import Console  # noqa: E402
from rich.panel import Panel  # noqa: E402

config = Dynaconf(
    settings_files=["config.yaml"]
)

with open('.pidfile', 'w') as f:
    f.write(str(os.getpid()))

scaler = load('joblib/scaler.joblib')
cols = load('joblib/columns.joblib')
class_names = load('joblib/class_names.joblib')
grid_clf_acc = load('joblib/rfmodel_multiclass_new.joblib')

kafka_bootstrap_servers = ','.join(config.kafka.bootstrap_servers)
kafka_topic = config.kafka.topic

ident = f'{project} - {title} v:{version}'

console = Console()
console.print(Panel.fit(ident))
console.print(f'Kafka Bootstrap Servers: {kafka_bootstrap_servers}')
console.print(f'Kafka Topic: {kafka_topic}')

producer = KafkaProducer(bootstrap_servers=kafka_bootstrap_servers)
consumer = KafkaConsumer(kafka_topic, bootstrap_servers=kafka_bootstrap_servers)

rep_time = 60
time_to_report = time.time() + rep_time
attackers = {}
for msg in consumer:

    message = msg.value.decode('utf-8')
    message2 = ast.literal_eval(message)

    testing = [float(message2[i]) for i in cols]
    # test = pd.DataFrame([testing], columns = cols)
    test = pd.DataFrame(scaler.transform(
        np.asarray(testing).reshape(1, -1)), columns=cols)
    test_preds = grid_clf_acc.predict(test)
    print("FLOW ID:", message2['FLOW_ID'], "result: class", class_names[test_preds[0]])

    if test_preds[0] != 0:
        if message2["IPV4_SRC_ADDR"] not in attackers:
            attackers[message2["IPV4_SRC_ADDR"]] = {}
        if class_names[test_preds[0]] not in attackers[message2["IPV4_SRC_ADDR"]]:
            attackers[message2["IPV4_SRC_ADDR"]
                      ][class_names[test_preds[0]]] = 1
        else:
            attackers[message2["IPV4_SRC_ADDR"]]
            [class_names[test_preds[0]]] = attackers[message2["IPV4_SRC_ADDR"]][class_names[test_preds[0]]] + 1

    if time.time() >= time_to_report:
        if attackers:
            output = {"SOURCE": "ALGO112_v3", "SEVERITY": "10",
                      "DESCRIPTION": "DDoS Attack(s)", "DATA": attackers, "TIMESTAMP": time.time()}
            producer.send('detection-results',
                          json.dumps(output).encode('utf-8'))
            print(attackers)
            attackers = {}
        time_to_report = time.time() + rep_time
