FROM python:3.7-slim

ENV KAFKA_BOOTSTRAP_SERVERS=localhost:9092
ENV KAFKA_TOPIC=network-data

RUN apt-get update -y
RUN apt-get install git httpie jq -y

ARG NOCACHE=true
RUN git clone https://github.com/guard-project/RESTable.git /opt/cnit_ml
WORKDIR /opt/cnit_ml
RUN mv scripts/start.sh scripts/restable-start.sh
RUN pip install --no-cache-dir -r requirements.txt

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY joblib/ ./joblib/
COPY src/ ./src/
COPY scripts/ ./scripts/
COPY RESTable/settings.yaml ./
COPY config.yaml ./

CMD [ "/bin/bash", "scripts/restable-start.sh" ]
