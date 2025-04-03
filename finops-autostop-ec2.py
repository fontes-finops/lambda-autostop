import boto3

def lambda_handler(event, context):
    ec2 = boto3.client('ec2')
    
    action = event.get('action')
    tag_key = event.get('tagKey')
    tag_value = event.get('tagValue')

    print(f"Received action: {action}")
    print(f"Tag key: {tag_key}, Tag value: {tag_value}")

    if not action or not tag_key or not tag_value:
        return {"status": "error", "message": "Missing required parameters"}

    instance_state_filter = ['stopped'] if action == 'start' else ['running']

    try:
        response = ec2.describe_instances(
            Filters=[
                {'Name': f'tag:{tag_key}', 'Values': [tag_value]},
                {'Name': 'instance-state-name', 'Values': instance_state_filter}
            ]
        )
    except Exception as e:
        print(f"Error describing instances: {e}")
        return {"status": "error", "message": f"Error describing instances: {str(e)}"}

    instance_ids = [instance['InstanceId'] for reservation in response['Reservations'] for instance in reservation['Instances']]

    if not instance_ids:
        return {"status": "success", "message": f"No matching instances found for action: {action}"}

    try:
        if action == 'stop':
            ec2.stop_instances(InstanceIds=instance_ids)
            return {"status": "success", "message": f"Stopped instances: {instance_ids}"}
        
        elif action == 'start':
            print(f"Starting instances: {instance_ids}")
            ec2.start_instances(InstanceIds=instance_ids)
            
            # Aguarda 90 segundos para dar tempo do estado da instância atualizar
            import time
            time.sleep(90)

            try:
                states = ec2.describe_instances(InstanceIds=instance_ids)
                print(f"Instance states after start: {states}")

                return {"status": "success", "message": f"Started instances: {instance_ids}"}
            
            except Exception as e:
                print(f"Error checking instance state: {e}")
                return {"status": "warning", "message": f"Instances started, but could not verify status: {instance_ids}"}

        else:
            return {"status": "error", "message": "Invalid action"}
    
    except Exception as e:
        print(f"Error performing action '{action}' on instances: {e}")
        return {"status": "error", "message": f"Error performing action '{action}' on instances: {str(e)}"}
