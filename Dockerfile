FROM ubuntu:16.04
MAINTAINER Vinicius Dias <viniciusvdias@dcc.ufmg.br>

ENV CAIPIRINHA_HOME /usr/local/caipirinha
ENV CAIPIRINHA_CONFIG $CAIPIRINHA_HOME/conf/caipirinha-config.yaml


RUN apt-get update && apt-get install -y  \
     python-pip \
   && rm -rf /var/lib/apt/lists/*

WORKDIR $CAIPIRINHA_HOME
COPY . $CAIPIRINHA_HOME
RUN pip install -r $CAIPIRINHA_HOME/requirements.txt

CMD ["/usr/local/caipirinha/sbin/caipirinha-daemon.sh", "startf"]
