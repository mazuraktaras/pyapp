import json
import boto3
import os


def lambda_handler(event, context):
    asg_name = ''
    instance_warmup = 40

    client = boto3.client('autoscaling')
    response = client.start_instance_refresh(AutoScalingGroupName=asg_name,
                                             Preferences={'InstanceWarmup': instance_warmup,
                                                          'MinHealthyPercentage': 90, }, )

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
