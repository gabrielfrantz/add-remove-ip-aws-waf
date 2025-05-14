import boto3
import ipaddress
import os
import sys

ip_cidr = sys.argv[1]
action = sys.argv[2].lower()

if '/' not in ip_cidr:
    print(f"❌ ERRO: O IP '{ip_cidr}' está sem o barramento CIDR. Ex: 192.168.0.1/32")
    sys.exit(1)

try:
    ip_network = ipaddress.ip_network(ip_cidr, strict=False)
except ValueError:
    print(f"❌ ERRO: O valor '{ip_cidr}' não é um IP/CIDR válido. Ex: 192.168.0.1/32")
    sys.exit(1)

valid_prefixes_v4 = [8, 16, 24, 32]
valid_prefixes_v6 = [24, 32, 48, 56, 64, 128]

if isinstance(ip_network, ipaddress.IPv4Network):
    if ip_network.prefixlen not in valid_prefixes_v4:
        print(f"❌ ERRO: Prefixo CIDR '{ip_network.prefixlen}' inválido para IPv4. Use um dos seguintes: /8, /16, /24, /32")
        sys.exit(1)
#elif isinstance(ip_network, ipaddress.IPv6Network):
#    if ip_network.prefixlen not in valid_prefixes_v6:
#        print(f"❌ ERRO: Prefixo CIDR '{ip_network.prefixlen}' inválido para IPv6. Use um dos seguintes: /24, /32, /48, /56, /64, /128")
#        sys.exit(1)

region_name = os.environ['AWS_REGION']
ip_set_id = os.environ['AWS_WAF_IPSET_ID']
ip_set_name = os.environ['AWS_WAF_IPSET_NAME']
scope = 'REGIONAL'

waf = boto3.client('wafv2', region_name=region_name)

response = waf.get_ip_set(Name=ip_set_name, Scope=scope, Id=ip_set_id)
addresses = response['IPSet']['Addresses']
lock_token = response['LockToken']

if action == "adicionar":
    if ip_cidr in addresses:
        print(f"ERRO: O IP {ip_cidr} já está cadastrado no IPSet.")
        sys.exit(1)
    addresses.append(ip_cidr)
    print(f"P {ip_cidr} adicionado com sucesso.")

elif action == "remover":
    if ip_cidr not in addresses:
        print(f"ERRO: O IP {ip_cidr} não está presente no IPSet.")
        sys.exit(1)
    addresses.remove(ip_cidr)
    print(f"IP {ip_cidr} removido com sucesso.")

waf.update_ip_set(
    Name=ip_set_name,
    Scope=scope,
    Id=ip_set_id,
    Addresses=addresses,
    LockToken=lock_token
)
