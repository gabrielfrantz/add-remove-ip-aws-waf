import boto3
import os

region_name = os.environ['AWS_REGION']
country_exceptions_list_id = os.environ['AWS_WAF_COUNTRY_EXCEPTIONS_LIST_ID']
country_exceptions_list_name = os.environ['AWS_WAF_COUNTRY_EXCEPTIONS_LIST_NAME']
scope = 'REGIONAL'

waf = boto3.client('wafv2', region_name=region_name)

response = waf.get_ip_set(Name=country_exceptions_list_name, Scope=scope, Id=country_exceptions_list_id)
addresses = response['IPSet']['Addresses']

print(f"Total de IPs cadastrados no IPSet: {len(addresses)}\n")
print("Lista dos IPs cadastrados no IPSet:")
for ip in addresses:
    print(f"- {ip}")
