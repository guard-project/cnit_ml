FROM python:3.7-slim

RUN apt-get update -y
RUN apt-get install git httpie jq fish gcc g++ micro iputils-ping curl -y

RUN useradd -rm -d /home/guard -s /bin/bash -g root -G sudo -u 1001 guard 
USER guard

RUN bash -c "$(curl -fsSL https://raw.githubusercontent.com/alexcarrega/oh-my-bash/master/tools/install.sh)"

ARG NOCACHE=true
RUN git clone https://github.com/guard-project/RESTable.git /home/guard/cnit_ml
WORKDIR /home/guard/cnit_ml
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

ARG RESTable_PORT=9999
EXPOSE $RESTable_PORT
