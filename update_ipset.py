import boto3
import os
import sys

ip_address = sys.argv[1]  # Recebe IP via CLI
action = sys.argv[2]      # add ou remove
region_name=os.environ['AWS_REGION'] # Use sua região

waf = boto3.client('wafv2', region_name)  
ip_set_id = os.environ['AWS_WAF_IPSET_ID']
ip_set_name = os.environ['AWS_WAF_IPSET_NAME']
scope = 'REGIONAL'

# Busca o IPSet atual
response = waf.get_ip_set(Name=ip_set_name, Scope=scope, Id=ip_set_id)
addresses = response['IPSet']['Addresses']
lock_token = response['LockToken']

# Atualiza lista
if action == "add" and f"{ip_address}/32" not in addresses:
    addresses.append(f"{ip_address}/32")
elif action == "remove" and f"{ip_address}/32" in addresses:
    addresses.remove(f"{ip_address}/32")

# Aplica mudança
waf.update_ip_set(
    Name=ip_set_name,
    Scope=scope,
    Id=ip_set_id,
    Addresses=addresses,
    LockToken=lock_token
)
