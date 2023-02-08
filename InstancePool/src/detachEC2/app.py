import re
import boto3
import json
import boto3
import logging
import boto3
import datetime
import uuid
import time
AccessControlAllowOrigin="https://d1wzk0972nk23y.cloudfront.net"
logger = logging.getLogger()
logger.setLevel(logging.INFO)
class CustomError(Exception):
  pass


def process(event, context):
    try:
        logger.info(event)
        body=event['body']
        body= json.loads(body)
        pathParameters=event['pathParameters']
            
        userId=pathParameters['userid']

        instanceIds=body['instanceIds']
        regionIds=body['regionids']

      

    except:
        raise CustomError("Please check the parameters.")


    sqs = boto3.resource('sqs')
    queue = sqs.get_queue_by_name(QueueName='VBS_Cloud_MessageQueue')

    now_datetime = datetime.datetime.now()
    dateTimeStr = now_datetime.strftime("%Y-%m-%d/%H:%M:%S:%f")
    
    msgId=str(uuid.uuid4())

    logger.info("======== msgId ------")
    logger.info(msgId)

    logger.info("======== dateTimeStr ------")
    logger.info(dateTimeStr)

    
    parameter = {"regions" : regionIds,'instanceIds':instanceIds,'dateTimeStr':dateTimeStr,'userId':userId,'eventUUID':msgId}
    parameterStr = json.dumps(parameter)

    logger.info("======== parameterStr ------")
    logger.info(parameterStr)
    queue.send_message(
        MessageBody=parameterStr, 
        MessageAttributes={
        'ActionEvent': {
            'StringValue': 'DetachEC2',
            'DataType': 'String'
            },
        })
   
    
    ###########code here
    return "Detach Event Sent"
def lambda_handler(event, context):
    try:
        if ('body' in event.keys()) & ('pathParameters' in event.keys()):

                data=process(event, context)
                json_data = [{
                                "status":"success",
                                "data": data
                                
                              }]
                                
                
                return {
                'headers':{
                    "Access-Control-Allow-Headers" : "Content-Type",
                    "Access-Control-Allow-Origin": AccessControlAllowOrigin,
                    "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
                },
                'statusCode': 200,
                'body': json.dumps(json_data)
                }
        
        
        json_data=[{
            "status":'fail',
            "data":"Please check the parameters."
        }]
        return {
                'headers':{
                    "Access-Control-Allow-Headers" : "Content-Type",
                    "Access-Control-Allow-Origin": AccessControlAllowOrigin,
                    "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
                },
                'statusCode': 401,
                'body': json.dumps(json_data)
                }
    except Exception as e:
        
        logger.info(e)
        json_data = [{
                        "status":"fail",
                        "data":str(e)
                        }]
        return {
            "statusCode": 402,
            "body": json.dumps(json_data),
            "isBase64Encoded": False,
            'headers':{
                    "Access-Control-Allow-Headers" : "Content-Type",
                    "Access-Control-Allow-Origin": AccessControlAllowOrigin,
                    "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
                },
                
            }
    