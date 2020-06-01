#!/bin/bash

ssh-keygen -f ./keys/ssh_host_rsa_key -N '' -t rsa
ssh-keygen -f ./keys/ssh_host_dsa_key -N '' -t dsa
