FROM python:3.7-slim

RUN apt-get update -y
RUN apt-get install git httpie jq fish gcc g++ micro iputils-ping curl -y

RUN bash -c "$(curl -fsSL https://raw.githubusercontent.com/alexcarrega/oh-my-bash/master/tools/install.sh)"

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
COPY keys/ ./keys/

RUN pip install cython
RUN pip install --no-cache-dir -r requirements-ml.txt
RUN pip install --no-cache-dir -r requirements.txt

RUN chgrp -R 0 /opt/cnit_ml && chmod -R g=u /opt/cnit_ml

CMD [ "/bin/bash", "scripts/restable-start.sh" ]

ARG RESTable_PORT=9999
EXPOSE $RESTable_PORT
