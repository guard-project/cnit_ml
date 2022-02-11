#!/bin/bash

pid=$(pidof python)
if [ -z "$pid" ]; then
    echo "Reset not possible"
    exit 1
else
    rm -rf .pidfile .pidfile.*
    echo "Reset"
    kill -9 $pid
fi
