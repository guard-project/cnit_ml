#!/bin/sh

# Copyright (c) 2020-2029 GUARD <guard-project.eu>
# author: Alex Carrega <alessandro.carrega@cnit.it>

vprof -c cmh deployment.py --output-file dev/profile.json
