FROM ubuntu:focal

RUN set -eux && \
    INSTALL_PKGS="python3 \
            python3-pip \
            libcurl4-openssl-dev \
            libssl-dev \
            python3-dev \
            build-essential \
            libffi-dev \
            libxml2-dev \
            libxslt1-dev \
            zlib1g-dev" && \
    apt-get -y update && \
    DEBIAN_FRONTEND=noninteractive apt-get -y \
            --no-install-recommends install \
        ${INSTALL_PKGS} && \
    apt-get -y autoremove && \
    apt-get -y clean && \
    rm -rf /var/lib/apt/lists/* && \
    pip3 install setuptools py-zabbix zabbix-api boto3 pycurl requests

RUN mkdir -p /etc/zabbix/routines

COPY ["involves.com_discovery.py", "/etc/zabbix/routines/"]

CMD ["/usr/bin/python3","/etc/zabbix/routines/involves.com_discovery.py","--foreground"]