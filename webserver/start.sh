#!/bin/bash

mode=$1

port=7890
host="0.0.0.0"

export FLASK_APP=fb_web_ui.py

if [ "$mode" = "development" ] ; then
    export FLASK_ENV=development
    flask run \
        --reload \
        --port "$port" \
        --host "$host"
elif [ "$mode" = "production" ] ; then
    export FLASK_ENV=production
    flask run \
        --port "$port" \
        --host "$host"
fi
