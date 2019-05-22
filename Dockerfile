FROM docker.elastic.co/logstash/logstash:7.1.0 
LABEL authors="maus"
USER root
ARG PYTHON_VERSION='3.7.3'
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
    && cd / \
    && rm -rf Python-${PYTHON_VERSION}*

USER logstash
ADD .config ./config
ADD scripts ./scripts
RUN pip3.7 install --user -r ./scripts/requirements.txt
