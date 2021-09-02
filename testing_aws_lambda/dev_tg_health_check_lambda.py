import json
import boto3
import time


def lambda_handler(event, context):
    target_group_arn = 'arn:aws:elasticloadbalancing:eu-north-1:188178296807:targetgroup/test-tg/4e169a853d589c2d'
    sns_topic_arn = 'arn:aws:sns:eu-north-1:188178296807:message-from-lambda'
    build_proj_name = 'pyapp'

    # interval of checks in seconds to avoid retry timeout
    check_interval = 1

    health_status = None
    message = f'Lamda function exited with timeout limit {context.get_remaining_time_in_millis() / 1000} sec.'

    # initialize elbv2 client
    elb_client = boto3.client('elbv2')

    # initialize sns client
    sns_client = boto3.client('sns')

    # initialize codebuild client
    code_build_client = boto3.client('codebuild')

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
            # start codeBuild project
            response = code_build_client.start_build(projectName=build_proj_name)

            message = f'CodeBuild project Selenium started successfully'

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
                       Subject='App health Notification')

    return {
        'statusCode': 200,
        'body': json.dumps(f'Lambda function {context.function_name} completed.')
    }
