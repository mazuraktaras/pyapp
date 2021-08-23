import json
import boto3
import os
import urllib3


def lambda_handler(event, context):
    http = urllib3.PoolManager()
    url = os.environ['WEB_HOOK_URL']
    notification_types = os.environ['NOTIFICATION_TYPES']
    topicArn = os.environ['TOPIC_ARN']

    x = event["body"]
    y = json.loads(x)

    try:
        c = y["payload"]
        d = c["details"]
        e = json.loads(d)
        type = e["type"]
        stage = type.split(":")[1]
        status = type.split(":")[2]
    except:
        stage = "not pipeline"
        status = "not failed"

    if stage == "pipeline" and (status == "failed" or status == "starting"):
        h = c["content"]
        i = json.loads(h)
        j = i["execution"]
        app = j["application"]
        pipe = j["name"]

        # NOTIFICATION_TYPES = "email, msteams"
        sw_list = notification_types.split(',')

        if 'email' in sw_list:
            snsClient = boto3.client('sns')

            publishObject = f'Pipeline {pipe} for application {app} has status {status}'

            response = snsClient.publish(TopicArn=topicArn,
                                         Message=json.dumps(publishObject),
                                         Subject='Spinnaker Notification')

        if 'msteams' in sw_list:
            publishObject = {
                "text": f'Pipeline ***{pipe}*** for application **{app}** has status **{status}**'}  # "\"Build project **<project-name>** has <build-status>.\""

            encoded_msg = json.dumps(publishObject).encode('utf-8')
            resp = http.request('POST', url, body=encoded_msg)

    return {
        'statusCode': 200
    }

