FROM python:3.7-slim

ENV KAFKA_BOOTSTRAP_SERVERS=localhost:9092
ENV KAFKA_TOPIC=network-data

RUN apt-get update -y
RUN apt-get install git httpie jq -y

RUN git clone https://github.com/guard-project/RESTable.git /opt/cnit_ml
WORKDIR /opt/cnit_ml
RUN pip install --no-cache-dir -r requirements.txt

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY *.joblib ./
COPY *.py ./
COPY settings.yaml ./

CMD [ "/bin/bash", "run.sh" ]
