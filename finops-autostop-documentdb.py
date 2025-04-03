import boto3

def lambda_handler(event, context):
    # Cliente para o Amazon DocumentDB
    client = boto3.client('docdb')

    # Nome do cluster DocumentDB diretamente no código
    cluster_name = "ms-bureau-staging-documentdb-cluster"  # Substitua pelo nome correto do cluster

    try:
        print(f"Iniciando verificação para o cluster: {cluster_name}")

        # Buscar o cluster pelo nome
        response = client.describe_db_clusters(DBClusterIdentifier=cluster_name)
        print(f"Resposta do describe_db_clusters: {response}")

        if not response['DBClusters']:
            print(f"Cluster '{cluster_name}' não encontrado.")
            return {
                'statusCode': 404,
                'body': f"Cluster '{cluster_name}' não encontrado."
            }

        cluster = response['DBClusters'][0]  # Pegando o primeiro cluster encontrado
        cluster_status = cluster['Status']  # Status atual do cluster (ex: 'available', 'stopped')
        print(f"Status atual do cluster '{cluster_name}': {cluster_status}")

        # Verificar se é hora de parar ou iniciar o cluster com base no status atual
        if cluster_status == 'available':
            print(f"O cluster {cluster_name} está disponível. Tentando parar...")
            stop_response = client.stop_db_cluster(DBClusterIdentifier=cluster_name)
            print(f"Resposta do AWS ao parar o cluster: {stop_response}")
            return {
                'statusCode': 200,
                'body': f"Cluster '{cluster_name}' foi parado com sucesso."
            }
        elif cluster_status == 'stopped':
            print(f"O cluster {cluster_name} está parado. Tentando iniciar...")
            start_response = client.start_db_cluster(DBClusterIdentifier=cluster_name)
            print(f"Resposta do AWS ao iniciar o cluster: {start_response}")
            return {
                'statusCode': 200,
                'body': f"Cluster '{cluster_name}' foi iniciado com sucesso."
            }
        else:
            print(f"O cluster '{cluster_name}' está em um estado '{cluster_status}'. Nenhuma ação necessária.")
            return {
                'statusCode': 200,
                'body': f"Cluster '{cluster_name}' está em um estado '{cluster_status}'. Nenhuma ação realizada."
            }

    except client.exceptions.DBClusterNotFoundFault:
        print(f"Erro: Cluster '{cluster_name}' não encontrado.")
        return {
            'statusCode': 404,
            'body': f"Cluster '{cluster_name}' não encontrado no AWS DocumentDB."
        }
    except Exception as e:
        print(f"Erro ao executar a ação no cluster '{cluster_name}': {str(e)}")
        return {
            'statusCode': 500,
            'body': f"Ocorreu um erro ao processar o cluster '{cluster_name}': {str(e)}"
        }
