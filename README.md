### **AWS AutoStop: Reduzindo Custos com Lambda, EventBridge e Tags**

## **Introdução**  
Gerenciar custos na AWS pode ser um desafio, especialmente quando recursos ficam ligados sem necessidade. Para resolver isso, criamos uma automação que inicia e para instâncias do **Amazon RDS, EC2 e DocumentDB** com base em regras definidas no **Amazon EventBridge** e em **tags** atribuídas aos recursos. Com essa abordagem, você evita gastos desnecessários e garante que os serviços estejam ativos apenas quando necessário.  

---

## **Visão Geral**  
A solução é composta por três componentes principais:  

✅ **AWS Lambda** → Função responsável por iniciar ou parar os recursos conforme as regras.  
✅ **Amazon EventBridge** → Regras programadas que acionam a função Lambda nos horários definidos.  
✅ **Tags nos Recursos** → Definem quais instâncias devem ser iniciadas ou paradas automaticamente.  

---  

## **Configuração da Solução**  

### **1. Configuração do AWS Lambda**  
Criamos uma **função Lambda em Python** utilizando o **boto3** para interagir com os serviços da AWS. O código:  
✅ Verifica o status do recurso.  
✅ Decide se deve **iniciar** ou **parar** a instância com base nas **tags** atribuídas.  
✅ Gera logs para monitoramento.  

### **2. Configuração do EventBridge**  
Criamos **regras programadas** que acionam o Lambda nos horários desejados.  

📌 **Exemplo de regra de início (Dias úteis às 09h BR / 12h UTC):**  
```json  
{  
  "action": "start",  
  "tagKey": "instance-start-9h",  
  "tagValue": "true"  
}  
```  

📌 **Exemplo de regra de parada (Meia-noite BR / 03h UTC):**  
```json  
{  
  "action": "stop",  
  "tagKey": "instance-stop-0h",  
  "tagValue": "true"  
}  
```  

### **3. Configuração das Tags**  
Para que a automação funcione, adicionamos **tags** nos recursos que queremos controlar:  

| Tag | Função |  
|------|---------|  
| `instance-stop-{horariosugerido} = true` | Desliga o recurso automaticamente no horário sugerido. |  
| `instance-start-{horariosugerido} = true` | Inicia o recurso automaticamente no horário sugerido. |  

---  

## **Configuração do IAM**  
A função Lambda precisa de uma **Role IAM** com permissões adequadas para iniciar e parar instâncias.  

📌 **Política IAM mínima necessária:**  
```json  
{  
  "Version": "2012-10-17",  
  "Statement": [  
    {  
      "Effect": "Allow",  
      "Action": [  
        "ec2:StartInstances",  
        "ec2:StopInstances",  
        "rds:StartDBInstance",  
        "rds:StopDBInstance",  
        "docdb:StartDBInstance",  
        "docdb:StopDBInstance"  
      ],  
      "Resource": "*"  
    }  
  ]  
}  
```  

✅ Para melhorar a segurança, substitua `*` pelo **ARN** das instâncias específicas que você deseja controlar.  
✅ Crie uma **Role IAM** com essa política e anexe-a à função Lambda.  

---  

## **Funcionamento do AWS Lambda**  
O **fluxo do Lambda** segue estas etapas:  

1️⃣ **Recebe a chamada** do EventBridge.  
2️⃣ **Verifica as tags** atribuídas ao recurso.  
3️⃣ **Checa o status atual** do recurso (ligado ou desligado).  
4️⃣ **Executa a ação necessária** (`start` ou `stop`).  
5️⃣ **Gera logs** para monitoramento.  

📌 **Ações para cada serviço:**  
🔹 **EC2**: `stop_instances(instance_ids)` | `start_instances(instance_ids)`  
🔹 **RDS**: `stop_db_instance(DBInstanceIdentifier=instance_id)` | `start_db_instance(DBInstanceIdentifier=instance_id)`  
🔹 **DocumentDB**: `stop_db_instance(DBInstanceIdentifier=instance_id)` | `start_db_instance(DBInstanceIdentifier=instance_id)`  

---  

## **Benefícios da Automação**  
✅ **Redução de custos**: Evita que instâncias fiquem ligadas sem necessidade.  
✅ **Automação flexível**: Baseada em horários e **tags personalizadas**.  
✅ **Simples e escalável**: Fácil de adaptar para diferentes cenários.  

---  

## **📌 Código no GitHub**  
O código está disponível no repositório pessoal de FinOps no GitHub:  

🔗 **[GitHub - fontes-finops/lambda-autostop](https://github.com/fontes-finops/lambda-autostop)**  

🚀 **Agora sua solução está pronta para economizar custos na AWS!**  

