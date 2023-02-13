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

def calculatePoolAmount(zone):
    dynamodbClient = boto3.client('dynamodb')
    response =dynamodbClient.query(
    TableName='VBS_Instance_Pool',
    IndexName="gsi_zone_available_index",
    Select='ALL_PROJECTED_ATTRIBUTES',
    # ConsistentRead=True,
    ReturnConsumedCapacity='INDEXES',
    ScanIndexForward=False, # return results in descending order of sort key
    KeyConditionExpression='gsi_zone = :z And available= :y',
    ExpressionAttributeValues={":z": {"S": zone},":y": {"S": "true"}}
    )   
    registorCount_running=0
    registorCount_stopped=0
    
    

    running_standby_instanceItems=[]
    stopped_standby_instanceItems=[]
    for item in response['Items']:
        if (item['available']['S']=='true') & \
           ((item['userId']['S']=='HTC_RRTeam') or (item['userId']['S']=='')):
            region=item['region']['S']
            status=item['instanceStatus']['S']
            
            if status=='running':
                registorCount_running=registorCount_running+1
                running_standby_instanceItems.append(item)
               
            elif status=='stopped':
                registorCount_stopped=registorCount_stopped+1
                stopped_standby_instanceItems.append(item)
    
    response_false =dynamodbClient.query(
    TableName='VBS_Instance_Pool',
    IndexName="gsi_zone_available_index",
    Select='ALL_PROJECTED_ATTRIBUTES',
    # ConsistentRead=True,
    ReturnConsumedCapacity='INDEXES',
    ScanIndexForward=False, # return results in descending order of sort key
    KeyConditionExpression='gsi_zone = :z And available= :y',
    ExpressionAttributeValues={":z": {"S": zone},":y": {"S": "false"}}
    )   
    
    userInUse=response_false['Items']


    return registorCount_running,registorCount_stopped,len(userInUse),running_standby_instanceItems,stopped_standby_instanceItems,userInUse


def process(event, context):
    try:
            logger.info(event)
            body=event['body']
            body= json.loads(body)
            pathParameters=event['pathParameters']
            
    except:
        raise CustomError("Please check the parameters.")
    
    action=pathParameters['actionId']

    #########code here
    if action=='listPoolStaticsByZone':
        zone=body['zone']

        runningNum,stoppedNum,inUseNum,runningPoolItems,stoppedPoolItems,inUsePoolItems=calculatePoolAmount(zone)
        json_data={
            'runningNum':runningNum,
            'stoppedNum':stoppedNum,
            'inUseNum':inUseNum,
            'runningPoolItems':runningPoolItems,
            'stoppedPoolItems':stoppedPoolItems,
            'inUsePoolItems':inUsePoolItems
        }
        return json_data
    elif action=="userCostById":
        StartTime=body['startTime']
        EndTime=body['endTime']
        
        dynamodbClient=boto3.client('dynamodb')

        # response =dynamodbClient.query(
        # TableName='VBS_User_UsageAndCost',
        # IndexName="userId_datetime_index",
        # Select='ALL_PROJECTED_ATTRIBUTES',
        # # ConsistentRead=True,
        # ReturnConsumedCapacity='INDEXES',
        # ScanIndexForward=False, # return results in descending order of sort key
        # KeyConditionExpression='userId = :z And datetime = :y',
        # ExpressionAttributeValues={":z": {"S": userId},":y": {"S": "true"}}
        # )   
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

        table = dynamodb.Table('VBS_User_UsageAndCost')

        response = table.query(
            IndexName="userId_datetime_index",
            KeyConditionExpression=Key('id').eq(1)
        )



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
    