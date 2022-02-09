#!/bin/sh
# Copyright (c) 2020 GUARD

watchmedo auto-restart --patterns="*.py" --recursive bash -- scripts/start.sh $*
