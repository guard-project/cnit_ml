import ast
import json
import time
from os import environ

import pandas as pd
from joblib import load
from kafka import KafkaConsumer, KafkaProducer

scaler = load('scaler.joblib')
cols = load('columns.joblib')
grid_clf_acc = load('rfmodel.joblib')

kafka_bootstrap_servers = environ.get(
    'KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
kafka_topic = environ.get('KAFKA_TOPIC', 'network-data')

producer = KafkaProducer(bootstrap_servers=kafka_bootstrap_servers)
consumer = KafkaConsumer(
    kafka_topic, bootstrap_servers=kafka_bootstrap_servers)

counter = 0
for msg in consumer:

    message = msg.value.decode('utf-8')
    message2 = ast.literal_eval(message)

    testing = []
    for i in cols:
        testing.append(float(message2[i]))

    test = pd.DataFrame([testing], columns=cols)
    test = pd.DataFrame(scaler.transform(test), columns=test.columns)

    test_preds = grid_clf_acc.predict(test)

    if test_preds[0] == 0:
        print("FLOW ID:", message2['FLOW_ID'], "result: BENIGN/REGULAR FLOW")

    if test_preds[0] == 1:
        print("FLOW ID:", message2['FLOW_ID'], "result: DDOS ATTACK FLOW")
        ml_output = "ddos"
        counter = counter + 1
        output = {"SOURCE": "ALGO112", "SEVERITY": "10", "DESCRIPTION": "DDoS LOIC",
                  "DATA": {"SOURCE_IP": message2['IPV4_SRC_ADDR'], "SOURCE_PORT": message2['L4_SRC_PORT'],
                           "DESTINATION_IP": message2['IPV4_DST_ADDR'], "DESTINATION_PORT": message2['L4_DST_PORT'],
                           "PROTOCOL": message2['PROTOCOL_MAP']}, "TIMESTAMP": time.time()}
        producer.send('detection-results', json.dumps(output).encode('utf-8'))
