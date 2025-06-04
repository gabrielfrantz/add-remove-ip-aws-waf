# Automação de atualização de IP no AWS WAF via GitHub Actions para múltiplas contas da AWS

Este repositório automatiza a inclusão ou remoção de endereços IP em um **IPSet do AWS WAF**, utilizando:

- **GitHub Actions**
- **Python com Boto3**
- **Autenticação segura via OIDC + IAM Role da AWS**
- **Suporte a múltiplos ambientes (dev/prod)**
- **Suporte a múltiplos IPs IPv4**

---

## Funcionalidades

- **Adicionar um ou múltiplos IPs IPv4** em formato CIDR (ex: `192.168.0.1/32`)
- **Remover um ou múltiplos IPs IPv4** existentes
- **Validação rigorosa de IPv4** (rejeita IPv6)
- **Validação rigorosa de BlackList** (conforme IPSet configurado)
- **Relatórios detalhados** de cada operação

##  O que cada arquivo do repositório faz

### `update_ipset.py`

Script em Python que:
- Lê os IPs atuais cadastrados no IPSet do WAF
- **Adiciona ou remove um ou múltiplos IPs IPv4** conforme parâmetros fornecidos
- **Processa IPs separados por vírgula** em uma única operação
- **Valida apenas endereços IPv4** (rejeita IPv6)
- Atualiza o IPSet com o novo conjunto de endereços
- **Relatórios informativos** sobre cada IP processado

### `list_ips.py`

Script em Python que:
- Lista os IPs do IPSet
- Exibe o **total de IPs cadastrados**
- Uso opcional

### `.github/workflows/waf-manage-ip.yml`

Workflow do GitHub Actions que:
- É acionado manualmente (`workflow_dispatch`) com dois inputs:
  - `environment`: Ambiente a ser executado
  - `ip_address`: **IP único ou múltiplos IPs IPv4 separados por vírgula**
  - `action`: `adicionar` ou `remover`
- Assume uma **IAM Role na AWS via OIDC**
- Executa o script `update_ipset.py` com as permissões mínimas necessárias

---

## Exemplos de Uso

### Via GitHub Actions (Recomendado)
1. Vá até a aba **Actions** do repositório
2. Execute o workflow `Gerenciar IPs no WAF`
3. Preencha os campos:
   - `environment`: development ou production
   - `ip_address`: Exemplos abaixo
   - `action`: adicionar ou remover

### Exemplos de IPs para o campo `ip_address`:

#### IP Único
```
192.168.1.1/32
```

#### Múltiplos IPs (separados por vírgula)
```
192.168.1.1/32,10.0.0.1/32,172.16.0.1/24
```

#### Diferentes prefixos IPv4
```
192.168.1.0/24,10.0.0.0/8,172.16.0.0/16,203.0.113.1/32
```

### Exemplo de Saída do Script:
```
Processando 3 IP(s): 192.168.1.1/32, 10.0.0.1/32, 172.16.0.1/24
✅ IP 192.168.1.1/32 adicionado com sucesso.
⚠️  O IP 10.0.0.1/32 já está cadastrado no IPSet.
✅ IP 172.16.0.1/24 adicionado com sucesso.
```

---

## Pré-requisitos

### 1. **Criar IPSet no AWS WAF**
Crie manualmente via console. Anote essas informações para usar mais tarde:
- `IPSet ID`
- `IPSet Name`
- `Região`

### 2. **Criar IAM Role para o GitHub Actions**

#### Trust Policy (`trust-policy.json`)
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::<AWS_ACCOUNT_ID>:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
          "token.actions.githubusercontent.com:sub": "repo:USUARIOOUORGANIZACAO/REPOSITORIO:environment:AMBIENTE"
        }
      }
    }
  ]
}
```

### 3. **Criar Policy com o mínimo de acesso possível**
Substitua <REGIAO>, <ACCOUNT_ID>, <NOME_DO_IPSET_EXCEPTION>, <ID_DO_IPSET_EXCEPTION>,<NOME_DO_IPSET_BLOCK>, <ID_DO_IPSET_BLOCK>:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "wafv2:GetIPSet",
        "wafv2:UpdateIPSet"
      ],
      "Resource": [
        "arn:aws:wafv2:<REGIAO>:<ACCOUNT_ID>:regional/ipset/<NOME_DO_IPSET_EXCEPTION>/<ID_DO_IPSET_EXCEPTION>",
        "arn:aws:wafv2:<REGIAO>:<ACCOUNT_ID>:regional/ipset/<NOME_DO_IPSET_BLOCK>/<ID_DO_IPSET_BLOCK>"
      ]
    }
  ]
}
```

### 4. **Criar secrets para cada environment da AWS no repositório**
Acessar settings > environments > SEU-AMBIENTE > secrets > add environment secrets:
- `AWS_ROLE_TO_ASSUME`: Colocar o valor do ARN da IAM Role criada
- `AWS_REGION`: Colocar o valor da região do WAF criado na AWS
- `AWS_WAF_COUNTRY_EXCEPTIONS_LIST_ID`: Colocar o valor do ID do IP SET de exceptions
- `AWS_WAF_COUNTRY_EXCEPTIONS_LIST_NAME`: Colocar o valor do nome do IP SET de exceptions
- `AWS_WAF_MALICIOUS_LIST_ID`: Colocar o valor do ID do IP SET de malicious
- `AWS_WAF_MALICIOUS_LIST_NAME`: Colocar o valor do nome do IP SET de malicious

---

## 🎯 Especificações Técnicas

### Endereços IPv4 Suportados
- **Formato**: Apenas IPv4 com notação CIDR
- **Prefixos válidos**: `/1` até `/32`
- **Múltiplos IPs**: Separados por vírgula (sem espaços extras)
- **IPv6**: ❌ Não suportado (será rejeitado)
