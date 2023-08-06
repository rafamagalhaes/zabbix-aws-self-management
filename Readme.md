# Zabbix auto-gerenciado com ambiente na AWS
Neste repositório temos algumas rotinas que realizam a inclusão automática no Zabbix, de recursos que foram criados na AWS.

## Rotina de instalação de agente Zabbix em instâncias EC2 (ec2-install-zabbix-agent)
Nesta rotina, o script lista todas as intâncias EC2 de uma determinada região, verifica se há um container de agente Zabbix em estado "Running", se não houver, irá inicializar um, se houver, irá reportar.

### Como usar:
Deve ser criado no Zabbix um host chamado "Zabbix Routines" e esse host deverá conter um item chamado "log.install.agents" e deverá ser do tipo "Zabbix Trapper"

Após realizar o clone do repositório, deverá ser gerado a imagem do container que irá executar a rotina.

cd ec2-install-zabbix-agent
docker build -t ec2-install-zabbix-agent:latest .

Depois de gerado a imagem, devemos executar o container.

docker run --name ec2-install-zabbix-agent-routine -e AWS_ACCESS_KEY_ID=<AWS_ACCESS_KEY> -e AWS_SECRET_ACCESS_KEY=<AWS_SECRET_KEY> -e ZABBIX_URL=<ZABBIX_URL> -e ZABBIX_USER=<ZABBIX_USER> -e ZABBIX_PASSWORD=<ZABBIX_PASSWORD> -e REGISTRY_USERNAME=<REGISTRY_USERNAME> -e REGISTRY_PASSWORD=<REGISTRY_PASSWORD> -e ZBX_VERSION=<ZBX_VERSION> -e REGION=<AWS_REGION> -d ec2-install-zabbix-agent:latest

## Rotina de inclusão de novas URL do Route53 no Zabbix (add-new-url-zabbix)
Nesta rotina, o script lista todas as urls de uma determinada região e zona, verifica se as URLs listadas estão monitoradas, se não estiver, irá incluí-la no monitoramento, caso já esteja, irá reportar.

### Como usar:
Deve ser criado no Zabbix um host chamado "Zabbix Routines" e esse host deverá conter um item chamado "add.new.url" e deverá ser do tipo "Zabbix Trapper"

Após realizar o clone do repositório, deverá ser gerado a imagem do container que irá executar a rotina.

cd add-new-url-zabbix
docker build -t add-new-url-zabbix:latest .

Depois de gerado a imagem, devemos executar o container.

docker run --name add-new-url-zabbix-routine -e AWS_ACCESS_KEY_ID=<AWS_ACCESS_KEY> -e AWS_SECRET_ACCESS_KEY=<AWS_SECRET_KEY> -e ZABBIX_URL=<ZABBIX_URL> -e ZABBIX_USER=<ZABBIX_USER> -e ZABBIX_PASSWORD=<ZABBIX_PASSWORD> -e REGION=<AWS_REGION> -e DOMAIN=<DOMAIN_NAME> -e ZONE_ID=<ZONE_ID> -e STRING_TEST=<STRING_TEST> -e PROXY_ID=<PROXY_ID> -d add-new-url-zabbix:latest

## Rotina de inclusão de novas instâncias RDS no Zabbix (add-new-rds-instance)
Nesta rotina, o script lista todas as instâcias RDS de uma determinada região, verifica se as instâncias listadas estão monitoradas, se não estiver, irá incluí-la no monitoramento, caso já esteja, irá reportar.

### Como usar:
Deve ser criado no Zabbix um host chamado "Zabbix Routines" e esse host deverá conter um item chamado "log.rds.instance" e deverá ser do tipo "Zabbix Trapper"

Após realizar o clone do repositório, deverá ser gerado a imagem do container que irá executar a rotina.

cd add-new-url-zabbix
docker build -t add-new-rds-instance:latest .

Depois de gerado a imagem, devemos executar o container.

docker run --name add-new-rds-instance-routine -e AWS_ACCESS_KEY_ID=<AWS_ACCESS_KEY> -e AWS_SECRET_ACCESS_KEY=<AWS_SECRET_KEY> -e ZABBIX_URL=<ZABBIX_URL> -e ZABBIX_USER=<ZABBIX_USER> -e ZABBIX_PASSWORD=<ZABBIX_PASSWORD> -e REGION=<AWS_REGION> -e DOMAIN=<DOMAIN_NAME> -e PROXY_ID=<PROXY_ID> -d add-new-rds-instance:latest
