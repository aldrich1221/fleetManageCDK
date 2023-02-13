import re
import boto3
import json
import boto3
import logging
import boto3
import datetime
import uuid
AccessControlAllowOrigin="https://d1wzk0972nk23y.cloudfront.net"
logger = logging.getLogger()
logger.setLevel(logging.INFO)
class CustomError(Exception):
  pass


def unitTest_Enlarge_Stopped_Pool(regionId):
    
    sqs = boto3.resource('sqs')
    queue = sqs.get_queue_by_name(QueueName='VBS_Cloud_MessageQueue')

    now_datetime = datetime.datetime.now()
    dateTimeStr = now_datetime.strftime("%Y-%m-%d/%H:%M:%S:%f")
    
    msgId=str(uuid.uuid4())

    parameter = {"zone" : regionId,'dateTimeStr':dateTimeStr,'userId':'HTC_RRTeam','eventUUID':msgId}
    parameterStr = json.dumps(parameter)

    logger.info("======== parameterStr ------")
    logger.info(parameterStr)
    queue.send_message(
        MessageBody=parameterStr, 
        MessageAttributes={
        'ActionEvent': {
            'StringValue': 'Enlarge_Stopped_Pool',
            'DataType': 'String'
            },
        })

def unitTest_Enlarge_Running_Pool(regionId):
    
    sqs = boto3.resource('sqs')
    queue = sqs.get_queue_by_name(QueueName='VBS_Cloud_MessageQueue')

    now_datetime = datetime.datetime.now()
    dateTimeStr = now_datetime.strftime("%Y-%m-%d/%H:%M:%S:%f")
    
    msgId=str(uuid.uuid4())

    parameter = {"zone" : regionId,'dateTimeStr':dateTimeStr,'userId':'HTC_RRTeam','eventUUID':msgId}
    parameterStr = json.dumps(parameter)

    logger.info("======== parameterStr ------")
    logger.info(parameterStr)
    queue.send_message(
        MessageBody=parameterStr, 
        MessageAttributes={
        'ActionEvent': {
            'StringValue': 'Enlarge_Running_Pool',
            'DataType': 'String'
            },
        })

def unitTest_Shrink_Stopped_Pool(regionId):
    
    sqs = boto3.resource('sqs')
    queue = sqs.get_queue_by_name(QueueName='VBS_Cloud_MessageQueue')

    now_datetime = datetime.datetime.now()
    dateTimeStr = now_datetime.strftime("%Y-%m-%d/%H:%M:%S:%f")
    
    msgId=str(uuid.uuid4())

    parameter = {"zone" : regionId,'dateTimeStr':dateTimeStr,'userId':'HTC_RRTeam','eventUUID':msgId}
    parameterStr = json.dumps(parameter)

    logger.info("======== parameterStr ------")
    logger.info(parameterStr)
    queue.send_message(
        MessageBody=parameterStr, 
        MessageAttributes={
        'ActionEvent': {
            'StringValue': 'Shrink_Stopped_Pool',
            'DataType': 'String'
            },
        })

def unitTest_Shrink_Running_Pool(regionId):
    
    sqs = boto3.resource('sqs')
    queue = sqs.get_queue_by_name(QueueName='VBS_Cloud_MessageQueue')

    now_datetime = datetime.datetime.now()
    dateTimeStr = now_datetime.strftime("%Y-%m-%d/%H:%M:%S:%f")
    
    msgId=str(uuid.uuid4())

    parameter = {"zone" : regionId,'dateTimeStr':dateTimeStr,'userId':'HTC_RRTeam','eventUUID':msgId}
    parameterStr = json.dumps(parameter)

    logger.info("======== parameterStr ------")
    logger.info(parameterStr)
    queue.send_message(
        MessageBody=parameterStr, 
        MessageAttributes={
        'ActionEvent': {
            'StringValue': 'Shrink_Running_Pool',
            'DataType': 'String'
            },
        })
def unitTest_DetachEC2():
    
    sqs = boto3.resource('sqs')
    queue = sqs.get_queue_by_name(QueueName='VBS_Cloud_MessageQueue')

    now_datetime = datetime.datetime.now()
    dateTimeStr = now_datetime.strftime("%Y-%m-%d/%H:%M:%S:%f")
    
    msgId=str(uuid.uuid4())

    regions=['ap-east-1']
    instanceIds=['i-0c538be986c176718']
    userId='instancePoolTestUser'
    
    parameter = {"regions" : regions,'instanceIds':instanceIds,'dateTimeStr':dateTimeStr,'userId':userId,'eventUUID':msgId}
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
def process(event, context):
    try:
            logger.info(event)
            body=event['body']
            body= json.loads(body)
            pathParameters=event['pathParameters']
            
    except:
        raise CustomError("Please check the parameters.")

    #########code here
    ############# Enlarge Running Pool #####################
    
    # unitTest_Enlarge_Running_Pool('ap-east-1')
    unitTest_Enlarge_Stopped_Pool('ap-east-1')
    # unitTest_Shrink_Stopped_Pool('ap-east-1')
    # unitTest_Shrink_Running_Pool('ap-east-1')








    ###########code here
    return "good"
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
    