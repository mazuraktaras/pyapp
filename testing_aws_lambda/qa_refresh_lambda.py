import json
import boto3
import os


def lambda_handler(event, context):
    # sns topic arn to email notification
    sns_topic_arn = os.environ['SNS_TOPIC_ARN']
    # ASG name to refresh
    asg_name = os.environ['ASG_NAME']
    # instance warmup in seconds.
    instance_warmup = int(os.environ['WARM_UP'])

    # initialize autoscaling client
    autoscaling_client = boto3.client('autoscaling')
    # initialize sns client
    sns_client = boto3.client('sns')

    # start ASG instance refresh
    response = autoscaling_client.start_instance_refresh(AutoScalingGroupName=asg_name,
                                                         Preferences={'InstanceWarmup': instance_warmup,
                                                                      'MinHealthyPercentage': 90})

    # prepare message to notify
    publish_object = f'CodeBuild project Selenium ended successfully. ' \
                     f'Instance refresh started in the {asg_name} autoscaling group.'

    # publish message to email topic
    sns_client.publish(TopicArn=sns_topic_arn,
                       Message=json.dumps(publish_object),
                       Subject='CodeBuild project Selenium Notification')

    return {
        'statusCode': 200,
        'body': json.dumps(f'Lambda function {context.function_name} completed.')
    }
