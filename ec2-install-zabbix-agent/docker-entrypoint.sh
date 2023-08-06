#!/bin/bash

SSH_CERT= <PRIVATE_KEY_BASE64_ENCRYPTED>

echo $SSH_CERT | base64 --decode > /etc/zabbix/routines/.ssh/ec2.pem

chmod 600 /etc/zabbix/routines/.ssh/ec2.pem