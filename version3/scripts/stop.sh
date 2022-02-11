#!/bin/bash

if [ -f ".pidfile" ]; then
    kill -9 $(cat .pidfile)
    echo "Stopped"
    rm -f .pidfile .pidfile.*
else
    echo "Stop not possible"
    exit 1
fi
