#!/bin/sh
. venv/bin/activate
python -m gunicorn -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker -w 1 run:app &
