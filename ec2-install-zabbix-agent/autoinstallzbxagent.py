import boto3
import os
from netmiko import ConnectHandler
from zabbix_api import ZabbixAPI
from pyzabbix import ZabbixMetric, ZabbixSender, ZabbixResponse
import time

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

def install_zbx_agent():
    metrics = []
    allHosts = get_hosts()
    resuser = os.getenv('REGISTRY_USERNAME')
    respass = os.getenv('REGISTRY_PASSWORD')
    zbxversion = os.getenv('ZBX_VERSION')
    region = os.getenv('REGION')
    ec2 = boto3.resource('ec2', region_name=region)
    running_instances = ec2.instances.filter(Filters=[{
        'Name': 'instance-state-name',
        'Values': ['running']
    }])
    log = "INFO - Gerando lista de servidores da AWS..."
    m = ZabbixMetric("Zabbix Routines","log.install.agents",log)
    metrics.append(m)
    ZabbixSender("zabbix-proxy-local").send(metrics)
    for instance in running_instances:
        metrics = []
        for tags in instance.tags:
            if tags["Key"] == 'Name':
                instancename = tags["Value"]
        ip = instance.private_ip_address
        if "test" not in instancename:
            if (instancename != "monitoring"):
                if instancename not in allHosts:
                    device = {
                        'device_type': 'linux',
                        'host': ip,
                        'username': 'ubuntu',
                        'use_keys': True,
                        'key_file': '~/.ssh/ec2.pem',
                        }
                    try:
                        with ConnectHandler(**device) as net_connect:
                            resgistrylogin = f"sudo docker login <REGISTRY_NAME> -u {resuser} -p {respass}"
                            zbxinstall = f"sudo docker run --name zabbix-agent2 --restart unless-stopped --net=host -p 10050:10050 -v /var/run:/var/run:rw -v /sys:/sys -v /sys/fs/cgroup:/sys/fs/cgroup -v /:/rootfs:ro -e ZBX_HOSTNAME={instancename} -e ZBX_SERVER_HOST=10.10.0.27 -e ZBX_METADATA=Linux,Docker -e ZBX_HOSTNAMEITEM=system.hostname -e ZBX_TIMEOUT=30 -e ZBX_REFRESHACTIVECHECKS=60 --privileged -d <REGISTRY_NAME>/<IMAGE_NAME>:{zbxversion}"
                            getdockergroupid = "cat /etc/group | grep docker | awk -F':' '{print $3}'"
                            restartcontzbxagent = "sudo docker restart zabbix-agent2"
                            log = f"INFO - Efetuando login no registry no servidor {instancename}..."
                            m = ZabbixMetric("Zabbix Routines","log.install.agents",log)
                            metrics.append(m)
                            output = net_connect.send_command(resgistrylogin)
                            if "Login Succeeded" in output:
                                log = "INFO - Login realizado com sucesso!"
                                m = ZabbixMetric("Zabbix Routines","log.install.agents",log)
                                metrics.append(m)
                                log = f"INFO - Instalando Zabbix Agent2 no servidor {instancename}..."
                                m = ZabbixMetric("Zabbix Routines","log.install.agents",log)
                                metrics.append(m)
                                output = net_connect.send_command(zbxinstall)
                                if "docker run --help" in output:
                                    log = f"ERRO - Instalação falhou no servidor {instancename}: {output}"
                                    m = ZabbixMetric("Zabbix Routines","log.install.agents",log)
                                    metrics.append(m)
                                else:
                                    log = f"SUCESS - Agente Zabbix instalado com sucesso no servidor {instancename}"
                                    m = ZabbixMetric("Zabbix Routines","log.install.agents",log)
                                    metrics.append(m)
                                    log = f"INFO - Configurando o agente Zabbix do servidor {instancename} para monitorar o Docker..."
                                    m = ZabbixMetric("Zabbix Routines","log.install.agents",log)
                                    metrics.append(m)
                                    dockergid = net_connect.send_command(getdockergroupid)
                                    output = net_connect.send_command(f"sudo docker exec --user root -ti zabbix-agent2 bash -c 'groupadd --gid {dockergid} docker && usermod -aG docker zabbix'")
                                    if "does not exist" in output:
                                        log = f"ERRO - Configuração falhou no servidor {instancename}: {output}"
                                        m = ZabbixMetric("Zabbix Routines","log.install.agents",log)
                                        metrics.append(m)
                                    else:
                                        log = f"INFO - Configuração realizada com sucesso no servidor {instancename}"
                                        m = ZabbixMetric("Zabbix Routines","log.install.agents",log)
                                        metrics.append(m)
                                        log = f"INFO - Reiniciando o agente Zabbix no servidor {instancename}..."
                                        m = ZabbixMetric("Zabbix Routines","log.install.agents",log)
                                        metrics.append(m)
                                        output = net_connect.send_command(restartcontzbxagent)
                                        if "zabbix-agent2" in output:
                                            log = f"INFO - Agente Zabbix reiniciado com sucesso no servidor {instancename}"
                                            m = ZabbixMetric("Zabbix Routines","log.install.agents",log)
                                            metrics.append(m)
                                        else:
                                            log = f"ERRO - Falha na reinicialização do agente Zabbix no servidor {instancename}: {output}"
                                            m = ZabbixMetric("Zabbix Routines","log.install.agents",log)
                                            metrics.append(m)
                            else:
                                log = f"ERRO - Falha de login no registry no servidor {instancename}: {output}"
                                m = ZabbixMetric("Zabbix Routines","log.install.agents",log)
                                metrics.append(m)
                    except:
                        log = f"WARN - Não foi possivel conectar-se no servidor {instancename}"
                        m = ZabbixMetric("Zabbix Routines","log.install.agents",log)
                        metrics.append(m)
                else:
                    log = f"INFO - Servidor {instancename} já monitorado."
                    m = ZabbixMetric("Zabbix Routines","log.install.agents",log)
                    metrics.append(m)

        ZabbixSender("zabbix-proxy-local").send(metrics)

def main():
    while True:
        install_zbx_agent()
        time.sleep(84600)

if __name__ == '__main__':
    main()

    


