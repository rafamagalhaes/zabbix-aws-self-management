FROM ubuntu:focal

RUN set -eux && \
    INSTALL_PKGS="python3 \
            python3-pip" && \
    apt-get -y update && \
    DEBIAN_FRONTEND=noninteractive apt-get -y \
            --no-install-recommends install \
        ${INSTALL_PKGS} && \
    apt-get -y autoremove && \
    apt-get -y clean && \
    rm -rf /var/lib/apt/lists/* && \
    pip3 install py-zabbix zabbix-api boto3 netmiko

RUN mkdir -p /etc/zabbix/routines/.ssh

COPY ["docker-entrypoint.sh","/usr/bin/"]

RUN bash /usr/bin/docker-entrypoint.sh

COPY ["autoinstallzbxagent.py", "/etc/zabbix/routines/"]

CMD ["/usr/bin/python3","/etc/zabbix/routines/autoinstallzbxagent.py","--foreground"]