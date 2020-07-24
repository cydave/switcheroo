#!/bin/bash

if [ ! -d ./keys ]; then
    ./genkeys.sh
fi
exec python3 main.py
