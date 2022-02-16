#!/bin/bash

if [ -f ".pidfile" ]; then
    pid=$(cat .pidfile)
    kill -HUP $pid
    echo "Restarted"
else
    echo "Not possible to restart program" >&2
    exit 1
fi
