import re
import boto3
import json
import boto3
import logging
import boto3
import requests

runningThreshold=2
stoppedThreshold=2
AccessControlAllowOrigin="https://d1wzk0972nk23y.cloudfront.net"
logger = logging.getLogger()
logger.setLevel(logging.INFO)
class CustomError(Exception):
  pass

def getSnapshotID(contentid,region):
  baseUrl="https://vxtiwk095b.execute-api.us-east-1.amazonaws.com/prod/contents/"
 
  headers = {
        'Authorization':'Basic cnJ0ZWFtOmlsb3ZlaHRj',
        'accept': 'application/json' 
    }

  req = requests.get(
   baseUrl+contentid+"/"+region,
   headers=headers
    )
  resp_dict = req.json()
  logger.info("======== req ------")
  logger.info(resp_dict['snapshot_id'])
  return resp_dict['snapshot_id']
def releaseInstance(dbtable,instanceId,msgId,dateTimeStr):
    response = dbtable.update_item(
                Key={
                    'id':instanceId,
                },
                UpdateExpression="set eventId = :a and eventTime = :b and userId = :c and available = :d ",
                ExpressionAttributeValues={
                    ':a': msgId,  
                    ':b': dateTimeStr,
                    ':c': 'HTC_RRTeam',
                    ':d': 'true',
                },
                ReturnValues="UPDATED_NEW"
            )

def eventRecord(dbtable,instanceId,msgId,dateTimeStr,userId):
    response = dbtable.update_item(
                Key={
                    'id':instanceId,
                },
                UpdateExpression="set eventId = :a and eventTime = :b and userId = :c ",
                ExpressionAttributeValues={
                    ':a': msgId,  
                    ':b': dateTimeStr,
                    ':c': userId,
                },
                ReturnValues="UPDATED_NEW"
            )

def processEvent_attachEC2(message):
    action_event = message.message_attributes.get('ActionEvent').get('StringValue')
    dateTimeStr = message.message_attributes.get('DateTime').get('StringValue')
    userId = message.message_attributes.get('User').get('StringValue')
    msgId = message.message_attributes.get('EventUUID').get('StringValue')
    body_json=json.loads(message.body)
    zone=body_json['zone']
    amount=body_json['amount']
    region=''

    dynamodbClient = boto3.client('dynamodb')
    response =dynamodbClient.query(
    TableName='VBS_Instance_Pool',
    IndexName="gsi_zone_available_index",
    Select='ALL_PROJECTED_ATTRIBUTES',
    # ConsistentRead=True,
    ReturnConsumedCapacity='INDEXES',
    ScanIndexForward=False, # return results in descending order of sort key
    KeyConditionExpression='gsi_zone = :z And available= :y',
    ExpressionAttributeValues={":z": {"S": body_json['zone']},":y": {"S": "true"}}
    )   

    

    ################ query the pool info ##########################
    dynamodb_resource = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb_resource.Table('VBS_Instance_Pool')
    registorCount_running=0
    registorCount_stopped=0
    registeredInstances_Running=[]
    registeredInstances_Stopped=[]
    
    for item in response['Items']:
        if (item['available']['S']=='true') & \
           ((item['userId']['S']=='HTC_RRTeam') or (item['userId']['S']=='')):
            region=item['region']['S']
            status=item['status']['S']
            
            if status=='running':
                registorCount_running=registorCount_running+1
                registeredInstances_Running.append(item)
            elif status=='stopped':
                registorCount_stopped=registorCount_stopped+1
                registeredInstances_Stopped.append(item)
        
        if registorCount_running==body_json['amount']:
            break
    
    finalInstances=[]
    if registorCount_running+registorCount_stopped<amount:
        logger.info("======== attach Emergency ------")
        ###send Emergency
    
    elif registorCount_running>=amount:
        for item in registeredInstances_Running:
            eventRecord(table,item['instanceId']['S'],msgId,dateTimeStr,userId)
            finalInstances.append(item)
    else:
        for item in registeredInstances_Running:
            eventRecord(table,item['instanceId']['S'],msgId,dateTimeStr,userId)
            finalInstances.append(item)
        for item in registeredInstances_Stopped:
            eventRecord(table,item['instanceId']['S'],msgId,dateTimeStr,userId)
            finalInstances.append(item)

    ################ send Enlarge_Running_Pool###################
    
    ################ send Enlarge_Stopped_Pool###################

    
    ################ attach EBS volume###########################

    ec2Client = boto3.client('ec2')
    ec2Resource = boto3.resource('ec2')
    
    # BlockDeviceMappings=[{'DeviceName': '/dev/sda1',
    #                   'Ebs': {
    #                       'DeleteOnTermination': True,
    #                       'VolumeSize': 250,
                          
    #                   },}]
    BlockDeviceMappings=[]
    deviceName=['xvda','xvdb','xvdc','xvdd','xvde','xvdf','xvdg','xvdh','xvdi','xvdj','xvdk','xvdl','xvdm','xvdn','xvdo','xvdp','xvdq','xvdr','xvds','xvdt','xvdu','xvdv','xvdw','xvdx','xvdy','xvdz']
    blocki=0
    for appid in body_json['appIds']:
        snapshotid=getSnapshotID(appid,region)
        for item in finalInstances:
            response = ec2Client.create_volume(
            AvailabilityZone=item['instanceId']['zone'],
            Size=50,
            SnapshotId=snapshotid,
            VolumeType='standard',
            TagSpecifications=[
                {
                    'ResourceType': 'capacity-reservation',
                    'Tags': [
                        {
                            'Key': 'appId',
                            'Value': appid
                        },
                    ]
                },
            ],
           
            )
  
            VolumeId=response['VolumeId']
            volume = ec2Resource.Volume(VolumeId)

            response = volume.attach_to_instance(
                Device=deviceName[blocki],
                InstanceId=item['instanceId']['S'],
            )
        blocki=blocki+1
    


        
def usageCompute(instancesIds,dynamodbClient):
    response =dynamodbClient.query(
    TableName='VBS_Instance_Pool',
    IndexName="gsi_zone_available_index",
    Select='ALL_PROJECTED_ATTRIBUTES',
    # ConsistentRead=True,
    ReturnConsumedCapacity='INDEXES',
    ScanIndexForward=False, # return results in descending order of sort key
    KeyConditionExpression='instanceId = :z And available= :y',
    ExpressionAttributeValues={":z": {"S": instancesIds},":y": {"S": "true"}}
    ) 

def processEvent_detachEC2(message):
    action_event = message.message_attributes.get('ActionEvent').get('StringValue')
    dateTimeStr = message.message_attributes.get('DateTime').get('StringValue')
    userId = message.message_attributes.get('User').get('StringValue')
    msgId = message.message_attributes.get('EventUUID').get('StringValue')
    body_json=json.loads(message.body)
    instances_to_datach=body_json['instanceId']


    dynamodbClient = boto3.client('dynamodb')
    dynamodb_resource = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb_resource.Table('VBS_Instance_Pool')


    ### usage and cost Compute
    # usageCompute(instances_to_datach,dynamodbClient)    

    releaseInstance(table,instances_to_datach,msgId,dateTimeStr)


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
    for item in response['Items']:
        if (item['available']['S']=='true') & \
           ((item['userId']['S']=='HTC_RRTeam') or (item['userId']['S']=='')):
            region=item['region']['S']
            status=item['status']['S']
            
            if status=='running':
                registorCount_running=registorCount_running+1
               
            elif status=='stopped':
                registorCount_stopped=registorCount_stopped+1
        
    return registorCount_running,registorCount_stopped

def processEvent_Enlarge_Running_Pool(message):
    action_event = message.message_attributes.get('ActionEvent').get('StringValue')
    dateTimeStr = message.message_attributes.get('DateTime').get('StringValue')
    userId = message.message_attributes.get('User').get('StringValue')
    msgId = message.message_attributes.get('EventUUID').get('StringValue')
    body_json=json.loads(message.body)

    #####################query Pool Instance############
    runningNum,stoppedNum=calculatePoolAmount(body_json['zone'])
    lambdaclient = boto3.client('lambda')
    diff_running=runningNum-runningThreshold
    diff_stopped=stoppedNum-stoppedThreshold
    if diff_running<0:
        if diff_stopped>0:
            if abs(diff_stopped)-abs(diff_running)<0:
                print("startEC2()+createEC2")
            else:
                print("startEC2(abs(diff_running))")
        else:
            # createEC2(abs(diff_running)+abs(diff_stopped))
            # stope(abs(diff_stopped)) 
            for i in range(abs(diff_running)+abs(diff_stopped)):
                payload = { 
                    "pathParameters": { "userid":"HTC_RRTeam"},
                    "body":
                        { 
                            "ec2zone":body_json['zone'],
                            "ec2type":"t3.medium",
                            'userAMI':"withSteam",
                            'spot':False
                        } } 

                result = lambdaclient.invoke(FunctionName='Function_vbs_create_ec2',
                            InvocationType='RequestResponse',                                      
                            Payload=json.dumps(payload))

            
                    
    
    



def messageProcess(action_event,message):
    if action_event=='AttachEC2':
        processEvent_attachEC2(message)
    elif action_event=='DetachEC2':
        processEvent_detachEC2(message)


def queueProcess(queue):
    logger.info("=================queue========")
    logger.info(queue)
    # for message in queue.receive_messages(MessageAttributeNames=['ActionEvent']):
    for message in queue.receive_messages():
        
        # message=message_ori.copy()
        # message_ori.delete()
        logger.info("=================queueMessage========")
        logger.info(message)
        logger.info("=================queueMessage:message.message_attributes========")
        logger.info(message.message_attributes)
        # Get the custom author message attribute if it was set
        message_text = ''
        if message.message_attributes is not None:
            
            action_event = message.message_attributes.get('ActionEvent').get('StringValue')
            if action_event:
                messageProcess(action_event,message)
                message_text = ' ({0})'.format(action_event)
        
        
        # Print out the body and author (if set)
        logger.info("============================")
        logger.info('Hello, {0}!{1}'.format(message.body, message_text))
        print('Hello, {0}!{1}'.format(message.body, message_text))

        # Let the queue know that the message is processed
        message.delete()

def process(event, context):
    # try:
    #         logger.info(event)
    #         body=event['body']
    #         body= json.loads(body)
    #         pathParameters=event['pathParameters']
            
    # except:
    #     raise CustomError("Please check the parameters.")

    #########code here

    logger.info("============================")
    logger.info(event)
    sqs = boto3.client('sqs')
    sqs_Resource = boto3.resource('sqs')
    ###################### write event Log #######################
    queue_L1 = sqs_Resource.get_queue_by_name(QueueName='VBS_Cloud_MessageQueue_L1')
    queue_L2 = sqs_Resource.get_queue_by_name(QueueName='VBS_Cloud_MessageQueue_L2')
    queue_L3 = sqs_Resource.get_queue_by_name(QueueName='VBS_Cloud_MessageQueue_L3')
    Level1_Events=['AttachEC2']
    Level2_Events=['Enlarge_Stopped_Pool']
    Level3_Events=['Shrink_Running_Pool']
    for record in event['Records']:
        queue=None
        if record['messageAttributes']['ActionEvent']['stringValue'] in Level1_Events:
            queue=queue_L1
        elif record['messageAttributes']['ActionEvent']['stringValue'] in Level2_Events:
            queue=queue_L2
        elif record['messageAttributes']['ActionEvent']['stringValue'] in Level3_Events:
            queue=queue_L3
            
        logger.info("===============Send different Level=============")
        logger.info(record['messageAttributes']['ActionEvent']['stringValue'])
        logger.info(record['messageAttributes']['DateTime']['stringValue'])
        logger.info(record['messageAttributes']['User']['stringValue'])
        logger.info(record['messageAttributes']['EventUUID']['stringValue'])
        queue.send_message(
            MessageBody=record['body'], 
            MessageAttributes={
            'ActionEvent': {
                'StringValue': record['messageAttributes']['ActionEvent']['stringValue'],
                'DataType': 'String'
                },
            'DateTime': {
                'StringValue': record['messageAttributes']['DateTime']['stringValue'],
                'DataType': 'String'
                },
            'User': {
                'StringValue': record['messageAttributes']['User']['stringValue'],
                'DataType': 'String'
                },
            'EventUUID':{
                'StringValue': record['messageAttributes']['EventUUID']['stringValue'],
                'DataType': 'String'
            },
            })


    ###################### get highest priority unconsumed message in Log ###########



    logger.info("=============== begin to process queue =============")
    # queue_L1 = sqs_Resource.get_queue_by_name(QueueName='VBS_Cloud_MessageQueue_L1')
    queueProcess(queue_L1)
    # queue_L2 = sqs_Resource.get_queue_by_name(QueueName='VBS_Cloud_MessageQueue_L2')
    queueProcess(queue_L2)
    # queue_L3 = sqs_Resource.get_queue_by_name(QueueName='VBS_Cloud_MessageQueue_L3')
    queueProcess(queue_L3)
    


    ###########code here
    return "good"
def lambda_handler(event, context):
    try:
        # if ('body' in event.keys()) & ('pathParameters' in event.keys()):
        if True:
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
    