FROM python:3.7-slim

ENV KAFKA_BOOTSTRAP_SERVERS=localhost:9092
ENV KAFKA_TOPIC=network-data

RUN apt-get update -y
RUN apt-get install git httpie jq fish gcc g++ -y

ARG NOCACHE=true
RUN git clone https://github.com/guard-project/RESTable.git /opt/cnit_ml
WORKDIR /opt/cnit_ml
RUN mv scripts/start.sh scripts/restable-start.sh

COPY requirements.txt requirements-ml.txt
COPY joblib/ ./joblib/
COPY src/ ./src/
COPY scripts/ ./scripts/
COPY RESTable/settings.yaml ./
COPY config.yaml ./

RUN pip install cython
RUN pip install --no-cache-dir -r requirements-ml.txt
RUN pip install --no-cache-dir -r requirements.txt

CMD [ "/bin/bash", "scripts/restable-start.sh" ]
