import json
import boto3
import os


def lambda_handler(event, context):
    sns_topic_arn = os.environ['SNS_TOPIC_ARN']
    asg_name = os.environ['ASG_NAME']

    # initialize sns client
    sns_client = boto3.client('sns')

    message = event['Records'][0]['Sns']['Message']
    message = json.loads(message)

    name = message['name']

    state = message['state']

    status = state['status']
    reason = state.get('reason')

    if status == 'AVAILABLE':
        output_resources = message['outputResources']
        amis = output_resources['amis'][0]
        # image_id = amis['image']
        # image_name = amis['name']

        autoscaling_client = boto3.client('autoscaling')

        response = autoscaling_client.start_instance_refresh(AutoScalingGroupName=asg_name,
                                                             Preferences={'InstanceWarmup': 40,
                                                                          'MinHealthyPercentage': 90, })

    publish_object = f'EC2ImageBuilder pipeline {name} has status {status} Reason: {reason}'

    response = sns_client.publish(TopicArn=sns_topic_arn,
                                  Message=publish_object,
                                  Subject='EC2ImageBuilder notification')

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
