import json
import time
from os import environ

from kafka import KafkaProducer

source_type = environ.get('SOURCE_TYPE', 'attack')
kafka_bootstrap_servers = environ.get(
    'KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
kafka_topic = environ.get('KAFKA_TOPIC', 'network-data')

print(f'KAFKA_BOOTSTRAP_SERVERS: {kafka_bootstrap_servers}')
print(f'KAFKA_TOPIC: {kafka_topic}')
print(f'SOURCE_TYPE: {source_type}')

file = open(f'vdpi_output_eth0_{source_type}_22Jun21.log', 'r')
# file = open('vdpi_output_eth0_normal_22Jun21.log', 'r')
# old
# file = open('vdpi_output_13Apr21.log', 'r')
# file = open('vdpi_output_22Jun21_3.log', 'r')

lines = file.read().splitlines()
file.close()

producer = KafkaProducer(bootstrap_servers=kafka_bootstrap_servers)
counter = 0
for line in lines:
    print(line)
    producer.send(kafka_topic, json.dumps(json.loads(line)).encode('utf-8'))
    time.sleep(0.05)
