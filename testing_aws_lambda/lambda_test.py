import os
import urllib3
import json


def lambda_handler(event, context):
    http = urllib3.PoolManager()

    url = os.environ['WEB_HOOK_URL']

    # TODO implement

    body = event['body']
    payload = json.loads(body)['payload']

    details = payload['details']
    details_parsed = json.loads(details)
    type_ = details_parsed['type']
    stage = type_.split(":")[1]
    status = type_.split(":")[2]

    publishObject = {
        "text": f'{stage}---{status}'
    }
    encoded_msg = json.dumps(publishObject).encode('utf-8')
    resp = http.request('POST', url, body=encoded_msg)

    return {
        'statusCode': 200,
        'body': json.dumps(f'{stage}---{status}----{url}')
    }
#