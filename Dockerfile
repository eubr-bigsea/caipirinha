FROM python:3.7.3-alpine3.9 as base

FROM base as pip_builder
RUN apk add --no-cache gcc musl-dev g++
COPY requirements.txt /
RUN pip install -r /requirements.txt

FROM base
LABEL maintainer="Vinicius Dias <viniciusvdias@dcc.ufmg.br>, Guilherme Maluf <guimaluf@dcc.ufmg.br>"

ENV CAIPIRINHA_HOME /usr/local/caipirinha
ENV CAIPIRINHA_CONFIG $CAIPIRINHA_HOME/conf/caipirinha-config.yaml

COPY --from=pip_builder /usr/local /usr/local
WORKDIR $CAIPIRINHA_HOME
COPY . $CAIPIRINHA_HOME/

CMD ["/usr/local/caipirinha/sbin/caipirinha-daemon.sh", "docker"]
