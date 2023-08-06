from zabbix_api import ZabbixAPI
from pyzabbix import ZabbixMetric, ZabbixSender, ZabbixResponse
import boto3
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
    zapi = connect_zbx_api()
    hosts = zapi.host.get({"output": ["host"]})
    host_list = []
    for host in hosts:
        host_list.append(host['host'])

    return host_list

def get_rds_instances():
    region = os.getenv('REGION')
    metrics = []
    rds_list = []
    log = "INFO - Gerando lista de servidores da AWS..."
    m = ZabbixMetric("Zabbix Routines","log.rds.instance",log)
    metrics.append(m)
    ZabbixSender("zabbix-proxy-local").send(metrics)
    rdsClientVirginia = boto3.client('rds', region_name=region)
    allDatabases = rdsClientVirginia.describe_db_instances()
    for db in allDatabases['DBInstances']:
        rds_list.append(db['DBInstanceIdentifier'])

    return rds_list

def add_rds_instance_zbx():
    aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    domain = os.getenv('DOMAIN')
    proxy = os.getenv('PROXY_ID')
    region = os.getenv('REGION')
    zapi = connect_zbx_api()
    allHosts = get_hosts()
    allRDSinstances = get_rds_instances()
    for novo_host in allRDSinstances:
        metrics = []
        if novo_host in allHosts:
            log = f"INFO - Instância {novo_host} já cadastrada."
            m = ZabbixMetric("Zabbix Routines","log.rds.instance",log)
            metrics.append(m)
        else:
            insert_host = zapi.host.create({
                "host": novo_host,
                "interfaces": [{
                    "type": 1,
                    "main": 1,
                    "useip": 0,
                    "ip": "",
                    "dns": "zabbix-agent2-rds",
                    "port": "10050"
                }],
                "groups": [{
                    "groupid": "22"
                },
                {
                    "groupid": "23"
                },
                {
                    "groupid": "24"
                },
                {
                    "groupid": "28"
                }],
                "tags": [{
                    "tag": "Monitoring",
                    "value": "RDS"
                }],
                "templates": [{
                    "templateid": "11297"
                },
                {
                    "templateid": "10320"
                }
                ],
                "macros": [{
                    "macro": "{$AWS_ACCESS_KEY}",
                    "value": aws_access_key
                },
                {
                    "macro": "{$AWS_SECRET_KEY}",
                    "value": aws_secret_key
                },
                {
                    "macro": "{$MYSQL.DSN}",
                    "value": f"{novo_host}.{domain}"
                },
                {
                    "macro": "{$REGION}",
                    "value": region
                }
                ],
                "proxy_hostid": proxy                
            })
            log = f"SUCESS - Instância {novo_host} cadastrada com sucesso!"
            m = ZabbixMetric("Zabbix Routines","log.rds.instance",log)
            metrics.append(m)
        ZabbixSender("zabbix-proxy-local").send(metrics)

def main():
    while True:
        add_rds_instance_zbx()
        time.sleep(84600)

if __name__ == '__main__':
    main()