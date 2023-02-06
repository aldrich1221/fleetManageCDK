import re
import boto3
import json
import boto3
import logging
import boto3
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
        regionId=pathParameters['regionid']
        appIds=body['appIds']
        amount=body['amount']


    except:
        raise CustomError("Please check the parameters.")

    #########code here
    ##instance pool db
    # dynamodb_resource = boto3.resource('dynamodb', region_name='us-east-1')
    # table = dynamodb_resource.Table('VBS_Instance_Pool')
    # dynamodb = boto3.client('dynamodb')
    # reponse=dynamodb.query(
    #     TableName='VBS_Instance_Pool',
    #     IndexName='user_region_Index',
    #     Select='ALL_PROJECTED_ATTRIBUTES',
    #     ConsistentRead=True,
    #     ReturnConsumedCapacity='INDEXES',
    #     ScanIndexForward=False, # return results in descending order of sort key
    #     Limit=amount,
    #     KeyConditionExpression='region = :region',
    #     ExpressionAttributeValues={":region": {"S": regionId}}
    # )


    sqs = boto3.resource('sqs')
    queue = sqs.get_queue_by_name(QueueName='VBS_Cloud_MessageQueue')

    queue.send_message(MessageBody='boto3', MessageAttributes={
    'Author': {
        'StringValue': 'Daniel',
        'DataType': 'String'
        }
    })
    

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
    