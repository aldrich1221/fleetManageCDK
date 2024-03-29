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


def startEC2(lambdaclient,ec2ids,ec2regions,userId):
    payload = { 
        "pathParameters": { "userid":userId,'actionid':'start'},
        "body":
            { 
                'ec2ids':ec2ids,
                'ec2regions':ec2regions
            } 
    } 
    lambdaclient.invoke(FunctionName='Function_vbs_manage_ec2',
                InvocationType='RequestResponse',                                      
                Payload=json.dumps(payload))

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

    now_datetime = datetime.datetime.now()
    dateTimeStr = now_datetime.strftime("%Y-%m-%d/%H:%M:%S:%f")
    
    msgId=str(uuid.uuid4())

    logger.info("======== msgId ------")
    logger.info(msgId)

    logger.info("======== dateTimeStr ------")
    logger.info(dateTimeStr)
    
   
    
    parameter = {"processCount":0,"zone" : regionId,'amount':amount,'appIds':appIds,'dateTimeStr':dateTimeStr,'userId':userId,'eventUUID':msgId}
    parameterStr = json.dumps(parameter)

    logger.info("======== parameterStr ------")
    logger.info(parameterStr)
    queue.send_message(
        MessageBody=parameterStr, 
        MessageAttributes={
        'ActionEvent': {
            'StringValue': 'AttachEC2',
            'DataType': 'String'
            },
        })
    ################### waiting for ownership############ 
    availableInstances=[]
    whileCount=0
    lambdaclient = boto3.client('lambda',region_name='us-east-1')
    while(True):
        time.sleep(1)
        dynamodbClient = boto3.client('dynamodb',region_name='us-east-1')
        # response =dynamodbClient.query(
        # TableName='VBS_Instance_Pool',
        # IndexName="gsi_zone_available_index",
        # Select='ALL_PROJECTED_ATTRIBUTES',
        # # ConsistentRead=True,
        # ReturnConsumedCapacity='INDEXES',
        # ScanIndexForward=False, # return results in descending order of sort key
        # KeyConditionExpression='gsi_zone = :z And available= :y',
        # ExpressionAttributeValues={":z": {"S": regionId},":y": {"S": "true"}}
        # )   

        response =dynamodbClient.query(
        TableName='VBS_Instance_Pool',
        IndexName="eventId-index",
        Select='ALL_PROJECTED_ATTRIBUTES',
        # ConsistentRead=True,
        ReturnConsumedCapacity='INDEXES',
        ScanIndexForward=False, # return results in descending order of sort key
        KeyConditionExpression='eventId = :z',
        ExpressionAttributeValues={":z": {"S": msgId}}
        )   

        logger.info("======== response ------")
        if len(response['Items'])>0:
            
            logger.info(response)
        availableInstanceCount=0
        availableInstances=[]
        for item in response['Items']:
            if (item['available']['S']=='true') & (item['userId']['S']==userId) & (item['eventId']['S']==msgId):

                newItem={
                    'instanceId':item['instanceId']['S'],
                    'instanceIp':item['instanceIp']['S'],
                    'available':item['available']['S'],
                    'userId':item['userId']['S'],
                    'eventId':item['eventId']['S'],
                    'zone':item['zone']['S'],
                    'region':item['region']['S']
                }
                logger.info("======== item['instanceIp']['S'] ------")
                logger.info(item['instanceIp']['S'])
                logger.info(item['instanceIp']['S']!='')
                if item['instanceIp']['S']!='':
                    availableInstances.append(newItem)
                    availableInstanceCount=availableInstanceCount+1
                # else:
                    
                #     startEC2(lambdaclient,[item['instanceId']['S']],[item['region']['S']],userId)

        if availableInstanceCount==amount:
            break
        whileCount=whileCount+1
        if whileCount>20:
            # raise CustomError("Error-From while Loop")
            
            waitForInfo = {"zone" : regionId,'amount':amount,'appIds':appIds,'dateTimeStr':dateTimeStr,'userId':userId,'eventUUID':msgId,'eventName':'AttachEC2'}
            attachEC2Response={
                'processingStatus':'doing',
                'data':waitForInfo
            }
            return attachEC2Response
            
    
    ##################### return the available instances #######################
    #######update the available to false and return available instances 
    dynamodb_resource = boto3.resource('dynamodb', region_name='us-east-1')

    table = dynamodb_resource.Table('VBS_Instance_Pool')
    for item in availableInstances:

        response = table.update_item(
                    Key={
                        'instanceId':item['instanceId'],
                        'region':item['region'],
                    },
                    UpdateExpression="set available = :r",
                    ExpressionAttributeValues={
                        ':r': 'false',  
                    },
                    ReturnValues="UPDATED_NEW"
                )
    attachEC2Response={
                'processingStatus':'done',
                'data':availableInstances
            }
    return attachEC2Response
    ###########code here
    
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
    