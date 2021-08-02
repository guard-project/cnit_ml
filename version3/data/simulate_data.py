from kafka import KafkaConsumer, KafkaProducer
from joblib import dump, load
import pandas as pd
import numpy as np
from os import listdir
import sys, re, csv, ast, json, time


#new from Panagiotis
file = open('vdpi_output_eth0_attack_22Jun21.log', 'r')
#file = open('vdpi_output_eth0_normal_22Jun21.log', 'r')
#old
#file = open('vdpi_output_13Apr21.log', 'r')
#file = open('vdpi_output_22Jun21_3.log', 'r')

lines = file.read().splitlines()
file.close()


producer = KafkaProducer(bootstrap_servers='guard3.westeurope.cloudapp.azure.com:29092')
counter=0
for line in lines:
    print(line)
    producer.send('network-data', json.dumps(json.loads(line)).encode('utf-8'))
    time.sleep(0.05)
    

