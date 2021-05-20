from kafka import KafkaConsumer
from kafka import KafkaProducer
import time


import pandas as pd
import numpy as np
from os import listdir
import sys, re, csv
import ast
import json

#ml methods and metrics
from sklearn.neural_network import MLPClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn import svm, tree
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import GridSearchCV
import sklearn.metrics as metrics
from sklearn.metrics import accuracy_score, balanced_accuracy_score, confusion_matrix, f1_score, recall_score, precision_score
from sklearn.preprocessing import StandardScaler
from skfeature.function.similarity_based import fisher_score
from sklearn.feature_selection import SelectKBest, chi2, f_classif, mutual_info_classif, f_regression
from sklearn.model_selection import train_test_split

from joblib import dump, load

scaler = load('scaler.joblib')
cols = load('columns.joblib')
grid_clf_acc= load('rfmodel.joblib')

producer = KafkaProducer(bootstrap_servers='130.251.17.128:9092')
consumer = KafkaConsumer('data', bootstrap_servers='130.251.17.128:9092')
counter=0
for msg in consumer:

    message = msg.value.decode('utf-8')
    message2=ast.literal_eval(message)

    testing=[]
    for i in cols:
        testing.append(float(message2[i]))

    print(testing)  
    test = pd.DataFrame ([testing], columns = cols)
    test = pd.DataFrame(scaler.transform(test), columns = test.columns)

    test_preds= grid_clf_acc.predict(test)

    if test_preds[0]==1:
        ml_output="ddos"
        counter = counter +1
        output={"SOURCE_IP":message2['IPV4_SRC_ADDR'], "SOURCE_PORT":message2['L4_SRC_PORT'], "DESTINATION_IP":message2['IPV4_DST_ADDR'],
                "DESTINATION_PORT":message2['L4_DST_PORT'], "PROTOCOL":message2['PROTOCOL_MAP'], "TIMESTAMP":time.time(), "ATTACK":"DDoS LOIC"}
        producer.send('ml', json.dumps(output).encode('utf-8'))

        

