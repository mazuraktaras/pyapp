import os
import time
from pprint import pprint

import boto3

ASG_NAME = 'DEV-asg'
INST_REFRESH_ID = '17b9585b-d570-40f1-aed2-39582809885e'
TIMEOUT = 60
TARG_GROUP_ARN = 'arn:aws:elasticloadbalancing:eu-north-1:188178296807:targetgroup/DEV-tg/8e9797c856a1f915'

client = boto3.client('autoscaling')

status = None
# status = 'Successful'
# print(os.environ['SSD'])
# print(os.environ['NEW'])
print(status)
print(time.perf_counter())
start_time = time.perf_counter()

while status != 'Successfu':
    print(time.perf_counter())

    if time.perf_counter() - start_time > TIMEOUT:
        print('I am gonna exiting!')
        print(f'Autoscaling group {ASG_NAME} instance refresh check exited with timeout {TIMEOUT} sec.')
        exit(1)
    #
    response = client.describe_instance_refreshes(
        AutoScalingGroupName=ASG_NAME,
        InstanceRefreshIds=[INST_REFRESH_ID],
        MaxRecords=1
    )

    status = response['InstanceRefreshes'][0]['Status']
    elapsed_time = TIMEOUT - (time.perf_counter() - start_time)
    print(f'Wait {ASG_NAME} refresh..... \nRefresh current status is \'{status}\' Time elapsed {elapsed_time} sec.')
    time.sleep(2)

    if status == 'Successful':
        print('Do stuff')
        print(f'Check DEV-tg health status..... Time elapsed {elapsed_time} sec.')

        # initialize elbv2 client
        elb_client = boto3.client('elbv2')

        while True:

            if time.perf_counter() - start_time > TIMEOUT:
                print('I am gonna exiting!')
                print(f'Autoscaling group {ASG_NAME} instance refresh check exited with timeout {TIMEOUT} sec.')
                exit(1)

            # get target group health
            response = elb_client.describe_target_health(TargetGroupArn=TARG_GROUP_ARN)

            # parse status
            health_status = response['TargetHealthDescriptions'][0]['TargetHealth']['State']

            if health_status == 'healthy':

                print('Target group DEV-tg is \'healthy\'. Pipeline continue to next stage')
                exit(0)

            elapsed_time = TIMEOUT - (time.perf_counter() - start_time)
            print(health_status, f'Time elapsed {elapsed_time} sec.')
            time.sleep(2)

        # break
