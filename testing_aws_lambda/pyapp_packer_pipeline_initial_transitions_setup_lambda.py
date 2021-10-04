import json
import boto3


def lambda_handler(event, context):
    code_pipeline_client = boto3.client('codepipeline')

    response = code_pipeline_client.disable_stage_transition(pipelineName='pyapp-packer-pipeline',
                                                             stageName='DEV-asg-Refresh',
                                                             transitionType='Outbound',
                                                             reason='Initially setted up to DISABLED state!'
                                                             )

    response = code_pipeline_client.disable_stage_transition(pipelineName='pyapp-packer-pipeline',
                                                             stageName='QA-asg-refresh-trigger',
                                                             transitionType='Outbound',
                                                             reason='Initially setted up to DISABLED state!'
                                                             )

    # response = code_pipeline_client.put_job_success_result(jobId=job_id)
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
