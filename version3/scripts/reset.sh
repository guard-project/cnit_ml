#!/bin/bash

pid=$(pid of python)
if [ -z "$pid" ]; then
    else "Reset not possible"
    exit 1
else
    killall $pid
    rm -rf .pidfile
    echo "Reset"
fi
