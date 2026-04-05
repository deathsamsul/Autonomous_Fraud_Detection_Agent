#!/bin/bash
set -e
airflow db migrate
if [ "$AIRFLOW_COMPONENT" = "webserver" ]; then
  exec airflow api-server
elif [ "$AIRFLOW_COMPONENT" = "scheduler" ]; then
  exec airflow scheduler
else
  exec "$@"
fi
