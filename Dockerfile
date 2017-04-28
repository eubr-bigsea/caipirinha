FROM ubuntu:16.04
MAINTAINER Vinicius Dias <viniciusvdias@dcc.ufmg.br>

# Install python and jdk
RUN apt-get update \
   && apt-get install -qy python-pip

# Install juicer
ENV CAIPIRINHA_HOME /usr/local/caipirinha
ENV CAIPIRINHA_CONFIG $CAIPIRINHA_HOME/conf/caipirinha-config.yaml
RUN mkdir -p $CAIPIRINHA_HOME/conf
RUN mkdir -p $CAIPIRINHA_HOME/sbin
RUN mkdir -p $CAIPIRINHA_HOME/caipirinha
ADD sbin $CAIPIRINHA_HOME/sbin
ADD caipirinha $CAIPIRINHA_HOME/caipirinha
ADD migrations $CAIPIRINHA_HOME/migrations
ADD logging_config.ini $STAND_HOME/logging_config.ini

# Install juicer requirements and entrypoint
ADD requirements.txt $CAIPIRINHA_HOME
RUN pip install -r $CAIPIRINHA_HOME/requirements.txt
EXPOSE 5000
CMD ["/usr/local/caipirinha/sbin/caipirinha-daemon.sh", "startf"]
