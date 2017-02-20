FROM python:2.7-onbuild
MAINTAINER Guilherme Maluf <guimalufb@gmail.com>

EXPOSE 3323
ENV LIMONERO_CONFIG="./caipirinha.yaml"
ENV PYTHONPATH="."
RUN chmod a+x "./run.sh"

CMD [ "./run.sh" ]
