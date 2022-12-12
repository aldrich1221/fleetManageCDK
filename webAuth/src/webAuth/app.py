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
            # body= json.loads(body)
            pathParameters=event['pathParameters']
            headers=event['headers']
    except:
        raise CustomError("Please check the parameters.")

    #########code here
    userid=headers['userid']
    password=headers['password']
    
    dynamodb_resource = boto3.resource('dynamodb', region_name='us-east-1')

        
    table = dynamodb_resource.Table('VBS_Enterprise_Info')
    response = table.scan(
                            FilterExpression=Attr('userid').eq(userid)
                        
                        )
    item = response['Items'][0]
    if  item.password==password:
        dynamodb_resource = boto3.resource('dynamodb', region_name='us-east-1')

                
        table = dynamodb_resource.Table('VBS_Enterprise_Info')
        
        temp_credentials={}
        response = table.query(
        KeyConditionExpression=Key('userid').eq('Enterprise_User_Service')
        )
        if 'Items' in response.keys():
            item = response['Items'][0]
            sts_client = boto3.client(
                'sts', aws_access_key_id=item['keypair_id'], aws_secret_access_key=item['keypair_secret'])
            try:
                session_name=f'enterpriseUser_session-{uuid4()}'
                response = sts_client.assume_role(
                    RoleArn=item['iam_role'], RoleSessionName=session_name)
                temp_credentials = response['Credentials']

                temp_credentials["login"]=True
                temp_credentials["apikey"]=item['keypair_id']
            except:
                raise
        return temp_credentials

    else:
        return {'login':False}
    ###########code here
    return "good"
def lambda_handler(event, context):
    try:
        if ('body' in event.keys()) & ('pathParameters' in event.keys()):

                data=process(event, context)
                json_data = [{
                                "status":"success",
                                "data": json.dumps(data)
                                
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
    