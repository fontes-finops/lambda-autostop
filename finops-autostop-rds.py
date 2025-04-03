import boto3

def lambda_handler(event, context):
    rds = boto3.client('rds')
    
    # Receber os parâmetros do EventBridge
    action = event.get('action')
    tag_key = event.get('tagKey')
    tag_value = event.get('tagValue')
    
    # Validar entrada
    if not action or not tag_key or not tag_value:
        return {"status": "error", "message": "Missing required parameters"}
    
    # Inicializar listas para instâncias e clusters
    matching_instances = []
    matching_clusters = []

    # Buscar instâncias RDS
    response = rds.describe_db_instances()
    instances = response['DBInstances']
    
    for instance in instances:
        instance_id = instance['DBInstanceIdentifier']
        instance_arn = instance['DBInstanceArn']
        
        # Verificar tags na instância
        tags_response = rds.list_tags_for_resource(ResourceName=instance_arn)
        tags = tags_response['TagList']
        
        has_tag = any(tag['Key'] == tag_key and tag['Value'] == tag_value for tag in tags)
        
        if has_tag:
            # Verificar estado atual
            if action == 'stop' and instance['DBInstanceStatus'] == 'available':
                matching_instances.append(instance_id)
            elif action == 'start' and instance['DBInstanceStatus'] == 'stopped':
                matching_instances.append(instance_id)
    
    # Buscar clusters RDS
    clusters_response = rds.describe_db_clusters()
    clusters = clusters_response['DBClusters']
    
    for cluster in clusters:
        cluster_id = cluster['DBClusterIdentifier']
        cluster_arn = cluster['DBClusterArn']
        
        # Verificar tags no cluster
        tags_response = rds.list_tags_for_resource(ResourceName=cluster_arn)
        tags = tags_response['TagList']
        
        has_tag = any(tag['Key'] == tag_key and tag['Value'] == tag_value for tag in tags)
        
        if has_tag:
            # Verificar estado atual
            if action == 'stop' and cluster['Status'] == 'available':
                matching_clusters.append(cluster_id)
            elif action == 'start' and cluster['Status'] == 'stopped':
                matching_clusters.append(cluster_id)
    
    # Log: Verificando instâncias e clusters correspondentes
    print(f"Matching instances: {matching_instances}")
    print(f"Matching clusters: {matching_clusters}")
    
    # Validar se existem instâncias ou clusters correspondentes
    if not matching_instances and not matching_clusters:
        return {"status": "success", "message": "No matching instances or clusters found"}
    
    # Realizar ação (start/stop) separadamente
    try:
        if action == 'stop':
            # Parar instâncias
            for instance_id in matching_instances:
                print(f"Stopping instance: {instance_id}")
                stop_response = rds.stop_db_instance(DBInstanceIdentifier=instance_id)
                print(f"Stop instance response: {stop_response}")
            
            # Parar clusters
            for cluster_id in matching_clusters:
                print(f"Stopping cluster: {cluster_id}")
                stop_response = rds.stop_db_cluster(DBClusterIdentifier=cluster_id)
                print(f"Stop cluster response: {stop_response}")
            
            message = f"Stopped instances: {matching_instances}, clusters: {matching_clusters}"
        
        elif action == 'start':
            # Iniciar instâncias
            for instance_id in matching_instances:
                print(f"Starting instance: {instance_id}")
                start_response = rds.start_db_instance(DBInstanceIdentifier=instance_id)
                print(f"Start instance response: {start_response}")
            
            # Iniciar clusters
            for cluster_id in matching_clusters:
                print(f"Starting cluster: {cluster_id}")
                start_response = rds.start_db_cluster(DBClusterIdentifier=cluster_id)
                print(f"Start cluster response: {start_response}")
            
            message = f"Started instances: {matching_instances}, clusters: {matching_clusters}"
        else:
            return {"status": "error", "message": "Invalid action"}
    except Exception as e:
        print(f"Error: {str(e)}")  # Log detalhado do erro
        return {"status": "error", "message": str(e)}
    
    return {"status": "success", "message": message}
