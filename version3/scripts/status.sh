#!/bin/bash

if [ -f .pidfile ]; then
    echo "Started"
else
    echo "Stopped"
fi
