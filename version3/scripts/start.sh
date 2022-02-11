#!/bin/bash

if [ -f ".pidfile" ]; then
    echo "Start not possible"
    exit 1
else
    python src/deployment.py
    echo "Started"
fi
