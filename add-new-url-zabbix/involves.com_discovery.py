import boto3
from zabbix_api import ZabbixAPI
from pyzabbix import ZabbixMetric, ZabbixSender, ZabbixResponse
import pycurl
import certifi
from io import BytesIO
import requests
import urllib3
import time
import os

def connect_zbx_api():
    url = os.getenv('ZABBIX_URL')
    username = os.getenv('ZABBIX_USER')
    password = os.getenv('ZABBIX_PASSWORD')

    zapi = ZabbixAPI(server = url)
    zapi.login(username, password)

    return zapi

def get_hosts():
    metrics = []
    log = f"INFO - Gerando lista de URLs já monitoradas."
    m = ZabbixMetric("Zabbix Routines","add.new.url",log)
    metrics.append(m)
    ZabbixSender("zabbix-proxy-local").send(metrics)
    zapi = connect_zbx_api()
    hosts = zapi.host.get({"output": ["host"]})
    host_list = []
    for host in hosts:
        host_list.append(host['host'])
    if bool(host_list):
        log = f"INFO - Lista de URLs já monitoradas gerada com sucesso."
        m = ZabbixMetric("Zabbix Routines","add.new.url",log)
        metrics.append(m)
        ZabbixSender("zabbix-proxy-local").send(metrics)
    else:
        log = f"ERRO - Falha ao gerar lista de URLs já monitoradas."
        m = ZabbixMetric("Zabbix Routines","add.new.url",log)
        metrics.append(m)
        ZabbixSender("zabbix-proxy-local").send(metrics)

    return host_list

def list_urls():
    domain = os.getenv('DOMAIN')
    zoneid = os.getenv('ZONE_ID')
    region = os.getenv('REGION')
    records = []
    metrics =[]
    client = boto3.client('route53', region_name=region)
    paginator = client.get_paginator('list_resource_record_sets')
    response = paginator.paginate(
        HostedZoneId=zoneid,
    )
    for record_set in response:
        for url in record_set['ResourceRecordSets']:
            if (url['Type'] == 'A') and ("ws." not in url['Name']):
                records.append(url['Name'][:-1])
    if domain in records[0]:
        log = f"INFO - Lista de URLs gerada com sucesso."
        m = ZabbixMetric("Zabbix Routines","add.new.url",log)
        metrics.append(m)
        ZabbixSender("zabbix-proxy-local").send(metrics)
    else:
        log = f"ERRO - Falha ao gerar lista de URLs."
        m = ZabbixMetric("Zabbix Routines","add.new.url",log)
        metrics.append(m)
        ZabbixSender("zabbix-proxy-local").send(metrics)

    return records

def add_url_zbx():
    string = os.getenv('STRING_TEST')
    proxy = os.getenv('PROXY_ID')
    allURLs = list_urls()
    zapi = connect_zbx_api()
    allHosts = get_hosts()
    for new_url in allURLs:
        metrics = []
        if new_url in allHosts:
            log = f"INFO - URL {new_url} já monitorada."
            m = ZabbixMetric("Zabbix Routines","add.new.url",log)
            metrics.append(m)
            ZabbixSender("zabbix-proxy-local").send(metrics)
        else:
            try:
                urllib3.disable_warnings()
                session = requests.Session()
                status = session.get(f"https://{new_url}", verify=False, timeout=15)
                if status.status_code == 200:
                    buffer = BytesIO()
                    c = pycurl.Curl()
                    c.setopt(c.CAINFO, certifi.where())
                    c.setopt(c.URL, f'{new_url}')
                    c.setopt(c.SSL_VERIFYPEER, 0)
                    c.setopt(c.WRITEDATA, buffer)
                    c.setopt(c.FOLLOWLOCATION, 1)
                    c.perform()
                    c.close()
                    body = buffer.getvalue()
                    test_active = body.decode('iso-8859-1')
                    if string in test_active:
                        insert_url = zapi.host.create({
                            "host": new_url,
                            "interfaces": [],
                            "groups": [{
                                "groupid": "25"
                            }],
                            "tags": [{
                                "tag": "Monitoring",
                                "value": "Web"
                            }],
                            "templates": [{
                                "templateid": "10627"
                            }],
                            "macros": [{
                                "macro": "{$URL}",
                                "value": f"https://{new_url}"
                            },
                            {
                                "macro": "{$STRING}",
                                "value": string
                            }],
                            "proxy_hostid": proxy                
                        })
                        log = f"SUCESS - URL {new_url} cadastrada com sucesso."
                        m = ZabbixMetric("Zabbix Routines","add.new.url",log)
                        metrics.append(m)
                        ZabbixSender("zabbix-proxy-local").send(metrics)
                    else:
                        log = f"WARN - URL {new_url} não é do Involves Stage."
                        m = ZabbixMetric("Zabbix Routines","add.new.url",log)
                        metrics.append(m)
                        ZabbixSender("zabbix-proxy-local").send(metrics)
                else:
                    log = f"WARN - URL {new_url} foi desativada."
                    m = ZabbixMetric("Zabbix Routines","add.new.url",log)
                    metrics.append(m)
                    ZabbixSender("zabbix-proxy-local").send(metrics)
            except:
                log = f"WARN - Não foi possivel conectar-se na URL {new_url}"
                m = ZabbixMetric("Zabbix Routines","add.new.url",log)
                metrics.append(m)
                ZabbixSender("zabbix-proxy-local").send(metrics)

def main():
    while True:
        add_url_zbx()
        time.sleep(84600)

if __name__ == '__main__':
    main()