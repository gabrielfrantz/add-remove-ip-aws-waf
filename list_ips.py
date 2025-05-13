import boto3
import os

region_name = os.environ['AWS_REGION']
ip_set_id = os.environ['AWS_WAF_IPSET_ID']
ip_set_name = os.environ['AWS_WAF_IPSET_NAME']
scope = 'REGIONAL'

waf = boto3.client('wafv2', region_name=region_name)

response = waf.get_ip_set(Name=ip_set_name, Scope=scope, Id=ip_set_id)
addresses = response['IPSet']['Addresses']

print("IPs cadastrados no IPSet:")
for ip in addresses:
    print(f"- {ip}")