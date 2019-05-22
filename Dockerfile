FROM docker.elastic.co/logstash/logstash:7.1.0 
LABEL authors="maus"
USER root
ARG PYTHON_VERSION='3.7.3'
# A sane person might ask you why I'm installing python3.7 in this container
# tl;dr slack's latest lib requires python3.7 for asyncio support and it's easier to
# use a elasticsearch->logstash container and build python over starting from python3.7
# and building a 
RUN yum install -y \
    wget \
    gcc make \
    libffi-devel \
    zlib-dev openssl-devel sqlite-devel bzip2-devel 
RUN wget https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tgz \
    && tar xvf Python-${PYTHON_VERSION}.tgz \
    && cd Python-${PYTHON_VERSION} \
    && ./configure --prefix=/usr/local \
    && make -j 8 \
    && make -j 8 altinstall \
    && rm -rf /usr/share/logstash/Python*

USER logstash
WORKDIR /usr/share/logstash
RUN rm -f ./pipeline/logstash.conf
RUN echo 'http.host: "127.0.0.1"' > ./config/logstash.yml
ADD pipeline/ ./pipeline/
COPY scripts/*.py ./scripts/
COPY scripts/requirements.txt ./scripts/
COPY scripts/config/config.json ./scripts//config/
RUN pip3.7 install --user -r ./scripts/requirements.txt
ENV SLACK_AUDIT_PATH=/usr/share/logstash/scripts/auditor.py
