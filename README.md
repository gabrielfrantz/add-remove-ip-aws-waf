# Automação de atualização de IP no AWS WAF via GitHub Actions para múltiplas contas da AWS

Este repositório automatiza a inclusão ou remoção de endereços IP em um **IPSet do AWS WAF**, utilizando:

- **GitHub Actions**
- **Python com Boto3**
- **Autenticação segura via OIDC + IAM Role da AWS**
- **Suporte a múltiplos ambientes (dev/prod)**

---

## Funcionalidades

- Listar os IPs cadastrados em um IPSet
- Adicionar um IP em formato CIDR (ex: `192.168.0.1/32`)
- Remover um IP existente
- Mostrar total de IPs cadastrados antes e depois da alteração

##  O que cada arquivo do repositório faz

### `update_ipset.py`

Script em Python que:
- Lê os IPs atuais cadastrados no IPSet do WAF.
- Adiciona ou remove um IP conforme o parâmetro fornecido (CIDR).
- Atualiza o IPSet com o novo conjunto de endereços.

### `list_ips.py`

Script em Python que:
- Lista os IPs do IPSet
- Exibe o **total de IPs cadastrados**

### `.github/workflows/update-waf.yml`

Workflow do GitHub Actions que:
- É acionado manualmente (`workflow_dispatch`) com dois inputs:
  - `environment`: Ambiente a ser executado.
  - `ip_address`: IP que será adicionado ou removido.
  - `action`: `adicionar` ou `remover`.
- Assume uma **IAM Role na AWS via OIDC**.
- Executa o script `update_ipset.py` com as permissões mínimas necessárias.

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
          "token.actions.githubusercontent.com:sub": "repo:USUARIO/REPOSITORIO:ENVIRONMENT"
        }
      }
    }
  ]
}
```

### 3. **Criar Policy com o mínimo de acesso possível**
Substitua <REGIAO>, <ACCOUNT_ID>, <NOME_DO_IPSET> e <ID_DO_IPSET>:
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
      "Resource": "arn:aws:wafv2:<REGIAO>:<ACCOUNT_ID>:regional/ipset/<NOME_DO_IPSET>/<ID_DO_IPSET>"
    }
  ]
}
```

### 4. **Criar secrets para cada environment da AWS no repositório**
Acessar settings > environments > SEU-AMBIENTE > secrets > add environment secrets:
- `AWS_ROLE_TO_ASSUME`: Colocar o valor do ARN da IAM Role criada
- `AWS_REGION`: Colocar o valor da região do WAF criado na AWS
- `AWS_WAF_IPSET_ID`: Colocar o valor do ID do IP SET
- `AWS_WAF_IPSET_NAME`: Colocar o valor do nome do IP SET

---

## Como usar
Vá até a aba Actions do repositório e execute o workflow `Atualizar IP no WAF`
Insira as seguintes informações:
- `environment`: development ou production (selecione a opção desejada)
- `ip_address`: ex: 192.168.0.1/32 (sempre com o barramento)
- `action`: adicionar ou remover (selecione a opção desejada)
