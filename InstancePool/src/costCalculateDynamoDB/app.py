import re
import boto3
import json
import boto3
import logging
import boto3
from boto3.dynamodb.conditions import Key, Attr
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
            
    except:
        raise CustomError("Please check the parameters.")

    #########code here
    aciton=pathParameters['acitonId']
    userid=pathParameters['userId']
    
    if aciton=='queryCostInPeriod':
        StartTime=body['StartTime']
        EndTime=body['EndTime']

        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

        table = dynamodb.Table('VBS_User_UsageAndCost')
        
        response = table.query(
                IndexName="userId_datetime_index",
                KeyConditionExpression=Key('userId').eq(userid) & Key('datetime').between(StartTime,EndTime)
            )
        return response
    
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
    