#!/bin/bash

if [ ! -d ./keys ]; then
    mkdir -p keys
    ssh-keygen -qf ./keys/ssh_host_rsa_key -N '' -t rsa
    ssh-keygen -qf ./keys/ssh_host_dsa_key -N '' -t dsa
fi
exec python3 main.py
