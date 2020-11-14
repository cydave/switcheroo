#!/bin/bash

[ -d ./keys ] || mkdir keys
[ -f ./keys/ssh_host_rsa_key ] || ssh-keygen -qf ./keys/ssh_host_rsa_key -N '' -t rsa
[ -f ./keys/ssh_host_dsa_key ] || ssh-keygen -qf ./keys/ssh_host_dsa_key -N '' -t dsa
exec python3 main.py
