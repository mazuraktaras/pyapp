import json
import boto3
import time
import os
import pprint


def lambda_handler(event, context):
    # TODO implement
    # print(context.get_remaining_time_in_millis()/1000/5)
    env = os.environ
    # print(type(env))
    # pprint.pprint(dict(env))
    code_pipeline_client = boto3.client('codepipeline')
    # response = code_pipeline_client.enable_stage_transition(pipelineName='dev-sonar-pack-pipeline',
    #                                                         stageName='Package-Build',
    #                                                         transitionType='Outbound'
    #                                                         )

    response = code_pipeline_client.disable_stage_transition(pipelineName='dev-sonar-pack-pipeline',
                                                             stageName='Package-Build',
                                                             transitionType='Outbound',
                                                             reason='Paused by EC2 ImageBuilder stage!'
                                                             )

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }

