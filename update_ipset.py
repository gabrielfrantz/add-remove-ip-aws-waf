import boto3
import ipaddress
import os
import sys

ip_input = sys.argv[1]
action = sys.argv[2].lower()

ip_list = [ip.strip() for ip in ip_input.split(',') if ip.strip()]

valid_ips = []
for ip_cidr in ip_list:
    if '/' not in ip_cidr:
        print(f"❌ ERRO: O IP '{ip_cidr}' está sem o barramento CIDR. Ex: 192.168.0.1/32")
        sys.exit(1)

    try:
        ip_network = ipaddress.ip_network(ip_cidr, strict=False)
    except ValueError:
        print(f"❌ ERRO: O valor '{ip_cidr}' não é um IP/CIDR válido. Ex: 192.168.0.1/32")
        sys.exit(1)

    valid_prefixes_v4 = list(range(1, 33))

    if isinstance(ip_network, ipaddress.IPv4Network):
        if ip_network.prefixlen not in valid_prefixes_v4:
            print(f"❌ ERRO: Prefixo CIDR '/{ip_network.prefixlen}' inválido para IPv4. Use um valor entre /1 e /32.")
            sys.exit(1)
        valid_ips.append(ip_cidr)
    else:
        print(f"❌ ERRO: O IP '{ip_cidr}' não é IPv4. Este script aceita apenas endereços IPv4.")
        sys.exit(1)

print(f"Processando {len(valid_ips)} IP(s): {', '.join(valid_ips)}")

region_name = os.environ['AWS_REGION']
scope = 'REGIONAL'

waf_exceptions_list_id = os.environ['AWS_WAF_EXCEPTIONS_LIST_ID']
waf_exceptions_list_name = os.environ['AWS_WAF_EXCEPTIONS_LIST_NAME']

malicious_list_id = os.environ.get('AWS_WAF_MALICIOUS_LIST_ID')
malicious_list_name = os.environ.get('AWS_WAF_MALICIOUS_LIST_NAME')

waf = boto3.client('wafv2', region_name=region_name)

if action == "adicionar" and malicious_list_id and malicious_list_name:
    response = waf.get_ip_set(Name=malicious_list_name, Scope=scope, Id=malicious_list_id)
    malicious_list_addresses = set(response['IPSet']['Addresses'])
    malicious_blocked_set = set(malicious_list_addresses)

    for ip in valid_ips:
        if ip in malicious_blocked_set:
            print(f"❌ ERRO: O IP {ip} está presente no IPSet de IPs maliciosos e não pode ser adicionado.")
            sys.exit(1)

response = waf.get_ip_set(Name=waf_exceptions_list_name, Scope=scope, Id=waf_exceptions_list_id)
addresses = response['IPSet']['Addresses']
lock_token = response['LockToken']

if action == "adicionar":
    added_ips = []
    existing_ips = []
    
    for ip_cidr in valid_ips:
        if ip_cidr in addresses:
            existing_ips.append(ip_cidr)
            print(f"⚠️ O IP {ip_cidr} já está cadastrado no IPSet.")
        else:
            addresses.append(ip_cidr)
            added_ips.append(ip_cidr)
            print(f"✅ O IP {ip_cidr} foi adicionado com sucesso.")
    
    if not added_ips:
        print("ℹ️ Nenhum IP novo foi adicionado.")
        sys.exit(1)

elif action == "remover":
    removed_ips = []
    not_found_ips = []
    
    for ip_cidr in valid_ips:
        if ip_cidr not in addresses:
            not_found_ips.append(ip_cidr)
            print(f"⚠️ O IP {ip_cidr} não está presente no IPSet.")
        else:
            addresses.remove(ip_cidr)
            removed_ips.append(ip_cidr)
            print(f"✅ O IP {ip_cidr} foi removido com sucesso.")
    
    if not removed_ips:
        print("ℹ️ Nenhum IP foi removido.")
        sys.exit(1)

waf.update_ip_set(
    Name=waf_exceptions_list_name,
    Scope=scope,
    Id=waf_exceptions_list_id,
    Addresses=addresses,
    LockToken=lock_token
)
