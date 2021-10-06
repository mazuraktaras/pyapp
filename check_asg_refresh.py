import time
from pprint import pprint

import boto3

ASG_NAME = 'DEV-asg'
INST_REFRESH_ID = '3d97896d-cb83-46da-a8db-5eb1cfe4f705'
TIMEOUT = 12

client = boto3.client('autoscaling')

status = 'Successful'

print(status)
print(time.perf_counter())
start_time = time.perf_counter()

for i in range(5):
    print('From script')
    print(time.perf_counter())
    time.sleep(1)
stop_time = time.perf_counter()
print(stop_time - start_time)
# while True:
#     print('From script')

while status == 'Successful':
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

    print('Wait ASG refresh.....')
    time.sleep(2)

    # pprint(response)
    # pprint(response['InstanceRefreshes'][0]['Status'])
    # time.sleep(3)
    # print(time.perf_counter())
    # print('Testing')
    # status = response['InstanceRefreshes'][0]['Status']
    # if status == 'Successful':
    #     print('Do stuff')
    #     #break
