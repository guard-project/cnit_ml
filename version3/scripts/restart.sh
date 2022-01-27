#!/bin/bash

if [ -f ".pidfile" ]; then
    kill -19 $(cat .pidfile)
    echo "Restarted"
    rm -f .pidfile
else
    echo "Not possible to restart program" >&2
    exit 1
fi
