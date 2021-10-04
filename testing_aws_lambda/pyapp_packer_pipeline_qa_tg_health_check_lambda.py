import json
import boto3
import time
import os


def lambda_handler(event, context):
    # load balancer's target group arn to check health
    target_group_arn = os.environ['TARG_GROUP_ARN']
    # sns topic arn to email notification
    sns_topic_arn = os.environ['SNS_TOPIC_ARN']
    # name of the CodeBuild project to start if the target group is healthy

    # interval of checks in seconds to avoid retry timeout
    check_interval = 1

    health_status = None

    message = f'Lamda function exited with timeout limit {context.get_remaining_time_in_millis() / 1000} sec.'

    # initialize elbv2 client
    elb_client = boto3.client('elbv2')

    # initialize sns client
    sns_client = boto3.client('sns')

    # initialize codepipline client
    code_pipeline_client = boto3.client('codepipeline')

    # compute loops count accordingly remaining timeout
    checks_count = int((context.get_remaining_time_in_millis() / 1000 - 2) / check_interval)
    print(checks_count)
    # check target health state in loop
    while checks_count > 0:

        # get target group health
        response = elb_client.describe_target_health(TargetGroupArn=target_group_arn)

        # parse stat
        health_status = response['TargetHealthDescriptions'][0]['TargetHealth']['State']

        if health_status == 'healthy':
            # enable codepipeline transititon after Package Build stage
            response = code_pipeline_client.enable_stage_transition(pipelineName='pyapp-packer-pipeline',
                                                                    stageName='QA-asg-refresh-trigger',
                                                                    transitionType='Outbound'
                                                                    )

            message = f'CodePipeline stage Selenium-DEV started successfully!'

            break
        # wait to avoid retry timeout
        time.sleep(check_interval)
        # decrement cycle counter
        checks_count -= 1

    # prepare message
    publish_object = f'Application health status is {health_status.upper()}. {message}'

    # publish to topic
    sns_client.publish(TopicArn=sns_topic_arn,
                       Message=json.dumps(publish_object),
                       Subject=f'Target group health Notification from {context.function_name}')

    return {
        'statusCode': 200,
        'body': json.dumps(f'Lambda function {context.function_name} completed.')
    }
