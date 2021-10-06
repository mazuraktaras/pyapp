import time
from pprint import pprint
import boto3

ASG_NAME = 'DEV-asg'
INST_REFRESH_ID = '3d97896d-cb83-46da-a8db-5eb1cfe4f705'
TIMEOUT = 60

client = boto3.client('autoscaling')

status = 'Successful'

while status == 'Successful':

    if time.perf_counter() > TIMEOUT:
        print('I am gonna exiting!')
        print(f'Autoscaling group {ASG_NAME} instance refresh check exited with timeout {TIMEOUT} sec.')
        exit(1)

    response = client.describe_instance_refreshes(
        AutoScalingGroupName=ASG_NAME,
        InstanceRefreshIds=[INST_REFRESH_ID],
        MaxRecords=1
    )

    # pprint(response)
    pprint(response['InstanceRefreshes'][0]['Status'])
    time.sleep(3)
    print(time.perf_counter())
    status = response['InstanceRefreshes'][0]['Status']
    if status == 'Successful':
        print('Do stuff')
        #break
