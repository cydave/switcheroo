#!/bin/bash

mkdir keys
ssh-keygen -f ./keys/ssh_host_rsa_key -N '' -t rsa >/dev/null
ssh-keygen -f ./keys/ssh_host_dsa_key -N '' -t dsa >/dev/null
