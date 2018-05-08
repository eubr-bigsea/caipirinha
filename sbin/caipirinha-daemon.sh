#!/usr/bin/env bash

# This script controls the caipirinha server daemon initialization, status reporting
# and termination
# TODO: rotate logs

usage="Usage: caipirinha-daemon.sh (start|docker|stop|status)"

# this sript requires the command parameter
if [ $# -le 0 ]; then
  echo $usage
  exit 1
fi

# parameter option
cmd_option=$1

# if unset set caipirinha_home to directory root
export CAIPIRINHA_HOME=${CAIPIRINHA_HOME:-$(cd `dirname $0`/..; pwd)}
echo ${CAIPIRINHA_HOME}

# get log directory
export CAIPIRINHA_LOG_DIR=${CAIPIRINHA_LOG_DIR:-${CAIPIRINHA_HOME}/logs}

# get pid directory
export CAIPIRINHA_PID_DIR=${CAIPIRINHA_PID_DIR:-/var/run}

mkdir -p ${CAIPIRINHA_PID_DIR} ${CAIPIRINHA_LOG_DIR}

# log and pid files
log=${CAIPIRINHA_LOG_DIR}/caipirinha-server-${USER}-${HOSTNAME}.out
pid=${CAIPIRINHA_PID_DIR}/caipirinha-server-${USER}.pid

case $cmd_option in
  (start)
    # set python path
    PYTHONPATH=${CAIPIRINHA_HOME}:${PYTHONPATH} \
      python ${CAIPIRINHA_HOME}/caipirinha/manage.py \
      db upgrade
    PYTHONPATH=${CAIPIRINHA_HOME}:${PYTHONPATH} nohup -- \
      python ${CAIPIRINHA_HOME}/caipirinha/runner/caipirinha_server.py \
      -c ${CAIPIRINHA_HOME}/conf/caipirinha-config.yaml >> $log 2>&1 < /dev/null &
    caipirinha_server_pid=$!

    # persist the pid
    echo $caipirinha_server_pid > $pid
    echo "Caipirinha server started, logging to $log (pid=$caipirinha_server_pid)"
    ;;

  (docker)
    trap "$0 stop" SIGINT SIGTERM
    # set python path
    PYTHONPATH=${CAIPIRINHA_HOME}:${PYTHONPATH} \
      python ${CAIPIRINHA_HOME}/caipirinha/manage.py \
      db upgrade
    PYTHONPATH=${CAIPIRINHA_HOME}:${PYTHONPATH} \
      python ${CAIPIRINHA_HOME}/caipirinha/runner/caipirinha_server.py \
      -c ${CAIPIRINHA_HOME}/conf/caipirinha-config.yaml &
    caipirinha_server_pid=$!

    # persist the pid
    echo $caipirinha_server_pid > $pid

    echo "Caipirinha server started, logging to $log (pid=$caipirinha_server_pid)"
    wait
    ;;

  (stop)
    if [ -f $pid ]; then
      TARGET_ID=$(cat $pid)
      if [[ $(ps -p ${TARGET_ID} -o comm=) =~ "python" ]]; then
        echo "stopping caipirinha server, user=${USER}, hostname=${HOSTNAME}"
        (pkill -SIGTERM -P ${TARGET_ID} && \
          kill -SIGTERM ${TARGET_ID} && \
          rm -f $pid )
      else
        echo "no caipirinha server to stop"
      fi
    else
      echo "no caipirinha server to stop"
    fi
    ;;

  (status)
    if [ -f $pid ]; then
      TARGET_ID=$(cat $pid)
      if [[ $(ps -p "${TARGET_ID}" -o comm=) =~ "python" ]]; then
        echo "caipirinha server is running (pid=${TARGET_ID})"
        exit 0
      else
        echo "$pid file is present (pid=${TARGET_ID}) but caipirinha server not running"
        exit 1
      fi
    else
      echo caipirinha server not running.
      exit 2
    fi
    ;;

  (*)
    echo $usage
    exit 1
    ;;
esac
