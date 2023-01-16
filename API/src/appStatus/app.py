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
            tableName=pathParameters['tablename']
            action=pathParameters['actionid']
    except:
        raise CustomError("Please check the parameters.")
    
    #########code here
    if tableName=='VBS_Instances_Information':
        dynamodb_resource = boto3.resource('dynamodb', region_name='us-east-1')

        table = dynamodb_resource.Table('VBS_Instances_Information')
        if action=='updateAPPStatus':
            try:
                instance_id=body["instanceId"]
                appstatus=body["appStatus"]

                response = table.update_item(
                            Key={
                                'id':instance_id,
                            },
                            UpdateExpression="set appStatus = :r",
                            ExpressionAttributeValues={
                                ':r': appstatus,  
                            },
                            ReturnValues="UPDATED_NEW"
                        )

                json_data = [{
                                "status":"success",
                                "data":response
                                }]
                logger.info("=========== Instance Table Response=============")
                logger.info(json_data)
                return json_data
            except:
                raise
 
      
        
    
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
    