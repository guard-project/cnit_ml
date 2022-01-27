#!/bin/bash

if [ -f ".pidfile" ]; then
    kill -9 $(cat .pidfile)
    echo "Stopped"
    rm -f .pidfile
else
    echo "Not possible to stop program" >&2
    exit 1
fi
