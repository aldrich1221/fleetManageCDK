import re
import boto3
import json
import boto3
import logging
import boto3
import requests
import datetime
import uuid
import time
runningThreshold=2
stoppedThreshold=2
dateTimeStrFormat = "%Y-%m-%d/%H:%M:%S:%f"
    
AccessControlAllowOrigin="https://d1wzk0972nk23y.cloudfront.net"
logger = logging.getLogger()
logger.setLevel(logging.INFO)
class CustomError(Exception):
  pass

def getSnapshotID(contentid,region):
  logger.info("======== getSnapshotID req ------")
  logger.info(contentid)
  logger.info(region)

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
  logger.info("======== response ------")
  logger.info(resp_dict['snapshot_id'])
  return resp_dict['snapshot_id']
def releaseInstance(dbtable,instanceId,region,msgId,dateTimeStr):

    
    response = dbtable.update_item(
                Key={
                    'instanceId':instanceId,
                    'region':region
                },
                UpdateExpression="set eventId = :a , eventTime = :b , userId = :c , available = :d ",
                ExpressionAttributeValues={
                    ':a': msgId,  
                    ':b': dateTimeStr,
                    ':c': 'HTC_RRTeam',
                    ':d': 'true',
                },
                ReturnValues="UPDATED_NEW"
            )

def eventRecord(dbtable,instanceId,zone,msgId,dateTimeStr,userId):
    response = dbtable.update_item(
                Key={
                    'instanceId':instanceId,
                    'region':zone
                },
                UpdateExpression="set eventId = :a ,eventTime = :b , userId = :c ",
                ExpressionAttributeValues={
                    ':a': msgId,  
                    ':b': dateTimeStr,
                    ':c': userId,
                },
                ReturnValues="UPDATED_NEW"
            )

def detach_EBS_Volume(instanceIds,regions):

    import boto3
    import csv
    import datetime
    import logging
    from os import environ
    import collections
    import time
    import sys


    def get_vol(instanceId, ec2):
        allvol=[]
        
        resp = ec2.describe_volumes(
            Filters=[{'Name':'attachment.instance-id','Values':[instanceId]}]
        )
        for volume1 in (resp["Volumes"]):
            for volume in volume1['Attachments']:
                resultVol = {
                }
             
             
                resultVol['vol_id'] = str(volume["VolumeId"])
                # resultVol['vol_size'] = str(volume["Size"])
                # resultVol['vol_type'] = str(volume["VolumeType"]) 
                resultVol['vol_device'] = str(volume['Device'])
    
                allvol.append(resultVol)
        return allvol
       
    for i in range(len(instanceIds)):
        instanceId=instanceIds[i]
        region=regions[i]
        boto_client = boto3.setup_default_session(region_name=region)
        boto_client = boto3.client('ec2')
        ec2 = boto3.client('ec2')
        ec2resource = boto3.resource('ec2', region_name=region)
        
        volsss = get_vol(instanceId, ec2)
        # print(volsss)
        for vol in volsss:
            if vol['vol_device']=='/dev/sda1':
                continue
            print(vol)
            # response = ec2.detach_volume(
            #     Device=vol['vol_device'],
            #     Force=True,
            #     InstanceId=instanceId,
            #     VolumeId=vol['vol_id'],
            
            # )

            volume = ec2resource.Volume(vol['vol_id'])
            volume.detach_from_instance(InstanceId=instanceId, Force=True)
            waiter = ec2.get_waiter('volume_available')
            waiter.wait(VolumeIds=[vol['vol_id']],)
            print (" INFO : Volume Detached")

            # Deleting Volume Device details already available
            volume.delete()
           
def attach_EBS_Volume(finalInstances,appIds,region):

    logger.info("======== attach_EBS_Volume ------")
    logger.info(appIds)
    logger.info(region)
    

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
    for appid in appIds:
        snapshotid=getSnapshotID(appid,region)
        for item in finalInstances:
            # response = ec2Client.create_volume(
              
            # AvailabilityZone=item['zone']['S'],
            # Size=50,
            # SnapshotId=snapshotid,
            # VolumeType='standard',
            # TagSpecifications=[
            #     {
            #         'ResourceType': 'capacity-reservation',
            #         'Tags': [
            #             {
            #                 'Key': 'appId',
            #                 'Value': appid
            #             },
            #         ]
            #     },
            # ],
           
            # )
  
            # VolumeId=response['VolumeId']
            # volume = ec2Resource.Volume(VolumeId)

            # response = volume.attach_to_instance(
            #     Device=deviceName[blocki],
            #     InstanceId=item['instanceId']['S'],
            # )

            Region=region
    
            boto_client = boto3.setup_default_session(region_name=Region)
            boto_client = boto3.client('ec2')
            ec2 = boto3.client('ec2')
            response = ec2.describe_instances()
            instance_dict = {}
        
            for reservation in response["Reservations"]:
                for instance in reservation["Instances"]:
                    if instance['State']['Name'] == "running":
                        if instance.__contains__("Tags"):
                            
                            instance_dict[instance["InstanceId"]] = instance["InstanceId"],instance['Placement']['AvailabilityZone']
                            
                        else:
                            
                            instance_dict[instance["InstanceId"]] = instance["InstanceId"],instance['Placement']['AvailabilityZone']
                        
                    elif instance['State']['Name'] == "stopped":
                        if instance.__contains__("Tags"):
                           
                            instance_dict[instance["InstanceId"]] = instance["InstanceId"],instance['Placement']['AvailabilityZone']
                            
                        else:
                            
                            instance_dict[instance["InstanceId"]] = instance["InstanceId"],instance['Placement']['AvailabilityZone']
                        
            # print()
            # print(instance_dict)
            iId = item['instanceId']['S']
            
            az = instance_dict[iId][1]
            
            size =50
            
            response= ec2.create_volume(
                        AvailabilityZone=az,
                        Encrypted=False,
                        #Iops=100,
                        #KmsKeyId='string',
                        Size=int(size),
                        SnapshotId=snapshotid,
                        VolumeType='gp2',    #standard'|'io1'|'gp2'|'sc1'|'st1',
                        DryRun=False,
                      
                        )
          
            # print("Volume ID : ", response['VolumeId'])
            # print("Volume ID : ", response['VolumeId'])
           
            waiter = ec2.get_waiter('volume_available')
        
            waiter.wait(VolumeIds=[response['VolumeId']],)
            # print (" INFO : Volume Detached")

            response= ec2.attach_volume(Device=deviceName[blocki], InstanceId=instance_dict[iId][0], VolumeId=response['VolumeId'])
            # print("State : ",response['State'])


        blocki=blocki+1
    
def processEvent_Shrink_Running_Pool(message):
    lambdaclient=boto3.client('lambda')
    # action_event = message.message_attributes.get('ActionEvent').get('StringValue')
    # dateTimeStr = message.message_attributes.get('DateTime').get('StringValue')
    # userId = message.message_attributes.get('User').get('StringValue')
    # msgId = message.message_attributes.get('EventUUID').get('StringValue')
    # body_json=json.loads(message.body)
    body_json=json.loads(message["body"])


    logger.info(body_json)
    dateTimeStr = body_json['dateTimeStr']
    userId = body_json['userId']
    msgId = body_json['eventUUID']
    zone=body_json['zone']
  
    runningNum,stoppedNum,runningPoolItems,stoppedPoolItems=calculatePoolAmount(zone)
    if runningNum>runningThreshold: 
        if stoppedNum>=stoppedThreshold:
            ec2ids,ec2regions=processPoolItemsToAPIFormat(runningPoolItems,runningNum-runningThreshold)
            deleteEC2(lambdaclient,ec2ids,ec2regions)
            sendEvent_Shrink_Stopped_Pool(zone)
    
        else:
            # ##To Stop
            # total=runningNum-runningThreshold
            # stopNum=total-(stoppedThreshold-stoppedNum)
            # deleteNum=total-stopNum
            # ec2ids,ec2regions=processPoolItemsToAPIFormat(runningPoolItems[:stopNum],stopNum)
            # stopEC2(lambdaclient,ec2ids,ec2regions)

            # ec2ids,ec2regions=processPoolItemsToAPIFormat(runningPoolItems[stopNum:],deleteNum)
            # deleteEC2(lambdaclient,ec2ids,ec2regions)
            ec2ids,ec2regions=processPoolItemsToAPIFormat(runningPoolItems,runningNum-runningThreshold)
            stopEC2(lambdaclient,ec2ids,ec2regions)
            sendEvent_Enlarge_Stopped_Pool(zone)
    else:
        checkProcessEventStatus(zone)

def processEvent_Shrink_Stopped_Pool(message):
    lambdaclient=boto3.client('lambda')
    # action_event = message.message_attributes.get('ActionEvent').get('StringValue')
    # dateTimeStr = message.message_attributes.get('DateTime').get('StringValue')
    # userId = message.message_attributes.get('User').get('StringValue')
    # msgId = message.message_attributes.get('EventUUID').get('StringValue')
    # body_json=json.loads(message.body)
    body_json=json.loads(message["body"])

    logger.info(body_json)
    dateTimeStr = body_json['dateTimeStr']
    userId = body_json['userId']
    msgId = body_json['eventUUID']
    zone=body_json['zone']
    


    runningNum,stoppedNum,runningPoolItems,stoppedPoolItems=calculatePoolAmount(zone)

    if stoppedNum>stoppedThreshold:
        if runningNum<runningThreshold:
            ##send
            ec2ids,ec2regions=processPoolItemsToAPIFormat(stoppedPoolItems,stoppedNum-stoppedThreshold)
            startEC2(lambdaclient,ec2ids,ec2regions)
            sendEvent_Enlarge_Running_Pool(zone)
        else:
            ec2ids,ec2regions=processPoolItemsToAPIFormat(stoppedPoolItems,stoppedNum-stoppedThreshold)
            deleteEC2(lambdaclient,ec2ids,ec2regions)
    else:
        checkProcessEventStatus(zone)


def processEvent_attachEC2(message):

    logger.info("======== processEvent_attachEC2 ------")
    logger.info(message)
    # action_event = message.message_attributes.get('ActionEvent').get('StringValue')
    # dateTimeStr = message.message_attributes.get('DateTime').get('StringValue')
    # userId = message.message_attributes.get('User').get('StringValue')
    # msgId = message.message_attributes.get('EventUUID').get('StringValue')
    
    # body_json=json.loads(message.body)
    body_json=json.loads(message["body"])


    logger.info(body_json)
    dateTimeStr = body_json['dateTimeStr']
    userId = body_json['userId']
    msgId = body_json['eventUUID']
    zone=body_json['zone']
    amount=body_json['amount']
    appIds=body_json['appIds']
    region=''
    send_Enlarge_Running_Pool=False
    send_Enlarge_Stopped_Pool=False

    dynamodbClient = boto3.client('dynamodb')
    lambdaclient=boto3.client('lambda')
   
    runningNum,stoppedNum,runningPoolItems,stoppedPoolItems=calculatePoolAmount(zone)

    

    ################ query the pool info and claim ownership##########################
    dynamodb_resource = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb_resource.Table('VBS_Instance_Pool')

    registorCount_running=runningNum
    registorCount_stopped=stoppedNum

    registeredInstances_Running=runningPoolItems
    registeredInstances_Stopped=stoppedPoolItems
    
 
   
    finalInstances=[]
    if registorCount_running+registorCount_stopped<amount:
        logger.info("======== attach Emergency ------")
        
        NewFastLaunchEC2Amount=amount-(registorCount_running+registorCount_stopped)

        processEvent_User_AttachEC2_Emergency(userId,zone,NewFastLaunchEC2Amount,appIds,registeredInstances_Running,registeredInstances_Stopped,msgId,dateTimeStr,table,lambdaclient)
       

        ###send Emergency
    else:
        alreadyAssignAmount=amount
        for item in registeredInstances_Running:
            eventRecord(table,item['instanceId']['S'],item['region']['S'],msgId,dateTimeStr,userId)
            finalInstances.append(item)
            region=item['region']['S']
            alreadyAssignAmount=alreadyAssignAmount-1
            if alreadyAssignAmount==0:
                break
            
        if alreadyAssignAmount>0:
            instancestartfromstopped=[]
            for item in registeredInstances_Stopped:
                eventRecord(table,item['instanceId']['S'],item['region']['S'],msgId,dateTimeStr,userId)
                finalInstances.append(item)
                instancestartfromstopped.append(item)
                alreadyAssignAmount=alreadyAssignAmount-1
                if alreadyAssignAmount==0:
                    break
            
            ec2ids,ec2regions=processPoolItemsToAPIFormat(instancestartfromstopped,len(instancestartfromstopped))
        
            startEC2(lambdaclient,ec2ids,ec2regions)

        send_Enlarge_Running_Pool=True     
        attach_EBS_Volume(finalInstances,appIds,region)

    # elif registorCount_running>=amount:
    #     for item in registeredInstances_Running:
    #         eventRecord(table,item['instanceId']['S'],item['region']['S'],msgId,dateTimeStr,userId)
    #         finalInstances.append(item)
    #     send_Enlarge_Running_Pool=True
    # elif((registorCount_running+registorCount_stopped>amount )& (registorCount_running<amount)):
    #     for item in registeredInstances_Running:
    #         eventRecord(table,item['instanceId']['S'],item['region']['S'],msgId,dateTimeStr,userId)
    #         finalInstances.append(item)
            
    #     for item in registeredInstances_Stopped:
    #         eventRecord(table,item['instanceId']['S'],item['region']['S'],msgId,dateTimeStr,userId)
    #         finalInstances.append(item)

    #     ec2ids,ec2regions=processPoolItemsToAPIFormat(registeredInstances_Stopped,registorCount_stopped)
        
    #     startEC2(lambdaclient,ec2ids,ec2regions)
       
    #     send_Enlarge_Running_Pool=True
    #     # send_Enlarge_Stopped_Pool=True

    sqs = boto3.resource('sqs')
    queue = sqs.get_queue_by_name(QueueName='VBS_Cloud_MessageQueue')
    
    ################ send Enlarge_Running_Pool###################
    if send_Enlarge_Running_Pool==True:

        sendEvent_Enlarge_Running_Pool(zone)
        
    ################ send Enlarge_Stopped_Pool###################
    if send_Enlarge_Stopped_Pool==True:
        now_datetime = datetime.datetime.now()
        dateTimeStr_new = now_datetime.strftime("%Y-%m-%d/%H:%M:%S:%f")
        
        msgId_new=str(uuid.uuid4())
        parameter = {"zone" : zone,'dateTimeStr':dateTimeStr_new,'userId':'HTC_RRTeam','eventUUID':msgId_new}
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


def sendEvent_Shrink_Running_Pool(zone):
    sqs = boto3.resource('sqs')
    queue = sqs.get_queue_by_name(QueueName='VBS_Cloud_MessageQueue')
    now_datetime = datetime.datetime.now()
    dateTimeStr_new = now_datetime.strftime("%Y-%m-%d/%H:%M:%S:%f")
    
    msgId_new=str(uuid.uuid4())
    parameter = {"zone" : zone,'dateTimeStr':dateTimeStr_new,'userId':'HTC_RRTeam','eventUUID':msgId_new}
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

def sendEvent_Shrink_Stopped_Pool(zone):
    sqs = boto3.resource('sqs')
    queue = sqs.get_queue_by_name(QueueName='VBS_Cloud_MessageQueue')
    now_datetime = datetime.datetime.now()
    dateTimeStr_new = now_datetime.strftime("%Y-%m-%d/%H:%M:%S:%f")
    
    msgId_new=str(uuid.uuid4())
    parameter = {"zone" : zone,'dateTimeStr':dateTimeStr_new,'userId':'HTC_RRTeam','eventUUID':msgId_new}
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

def sendEvent_Enlarge_Stopped_Pool(zone):
    sqs = boto3.resource('sqs')
    queue = sqs.get_queue_by_name(QueueName='VBS_Cloud_MessageQueue')
    now_datetime = datetime.datetime.now()
    dateTimeStr_new = now_datetime.strftime("%Y-%m-%d/%H:%M:%S:%f")
    
    msgId_new=str(uuid.uuid4())

    parameter = {"zone" : zone,'dateTimeStr':dateTimeStr_new,'userId':'HTC_RRTeam','eventUUID':msgId_new}
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

def sendEvent_Enlarge_Running_Pool(zone):
    sqs = boto3.resource('sqs')
    queue = sqs.get_queue_by_name(QueueName='VBS_Cloud_MessageQueue')
    now_datetime = datetime.datetime.now()
    dateTimeStr_new = now_datetime.strftime("%Y-%m-%d/%H:%M:%S:%f")
    
    msgId_new=str(uuid.uuid4())

    parameter = {"zone" : zone,'dateTimeStr':dateTimeStr_new,'userId':'HTC_RRTeam','eventUUID':msgId_new}
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
    
    


        
def usageCompute(instancesIds,instancesRegions,dynamodbClient,userId,msgId):
    logger.info("======== usageCompute------")
    logger.info(instancesIds)
    logger.info(instancesRegions)

    for i in range(len(instancesIds)):
        instancesId=instancesIds[i]
        region=instancesRegions[i]
        

        response =dynamodbClient.query(
        TableName='VBS_Instance_Pool',
        ReturnConsumedCapacity='INDEXES',
        ScanIndexForward=False, # return results in descending order of sort key
        KeyConditionExpression='instanceId = :z',
        ExpressionAttributeValues={":z": {"S": instancesId}}
        ) 

        logger.info("======== usageCompute reponse------")
        logger.info(response)

        currenttime=datetime.datetime.now()
        currenttimeStr =currenttime.strftime("%Y-%m-%d/%H:%M:%S:%f")
    
        for item in response['Items']:
            logger.info(item)
            if item['userId']['S']==userId:
                eventTime=item['eventTime']['S']
                
                dt_object = datetime.datetime.strptime(eventTime, dateTimeStrFormat)
                diff=currenttime-dt_object
                diff_totalseconds=diff.total_seconds()
                cost=diff_totalseconds*0.005

                # diffStr =diff.strftime("%Y-%m-%d/%H:%M:%S:%f")
                days = diff.days
                seconds = diff.seconds

                hours = seconds//3600
                minutes = (seconds//60) % 60

                diffStr=str(days)+' days '+str(hours)+' hours '+ str(minutes)+' minutes.'
                
                                
                response=dynamodbClient.put_item(TableName='VBS_User_UsageAndCost', Item={
                    'eventId':{'S':msgId},
                    'datetime':{'S':currenttimeStr},
                    'userId':{'S':userId},
                    'instanceId':{'S':item['instanceId']['S']},
                    'beginTime':{'S':eventTime},
                    'endTime':{'S':currenttimeStr},
                    'UsageTime':{'S':diffStr},
                    'UsageTime_totalseconds':{'S':str(diff_totalseconds)},
                    'UsageCost':{'S':str(cost)},
                    })

def processEvent_detachEC2(message):
    logger.info("======== processEvent_detachEC2 ------")
    logger.info("======== processEvent_detachEC2 ------")
    
    # action_event = message.message_attributes.get('ActionEvent').get('StringValue')
    # dateTimeStr = message.message_attributes.get('DateTime').get('StringValue')
    # userId = message.message_attributes.get('User').get('StringValue')
    # msgId = message.message_attributes.get('EventUUID').get('StringValue')
    # body_json=json.loads(message.body)
    body_json=json.loads(message["body"])
    instances_to_datach=body_json['instanceIds']
    regions=body_json['regions']

    dateTimeStr = body_json['dateTimeStr']
    userId = body_json['userId']
    msgId = body_json['eventUUID']


    dynamodbClient = boto3.client('dynamodb')
    dynamodb_resource = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb_resource.Table('VBS_Instance_Pool')


    ### usage and cost Compute
    usageCompute(instances_to_datach,regions,dynamodbClient,userId,msgId)  

    detach_EBS_Volume(instances_to_datach,regions)
    uniqueRegions=[]
    for i in range(len(instances_to_datach)):
        if regions[i] not in uniqueRegions:
            uniqueRegions.append(regions[i])
        releaseInstance(table,instances_to_datach[i],regions[i],msgId,dateTimeStr)
    for region in uniqueRegions:
        sendEvent_Shrink_Running_Pool(region)


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
        
    return registorCount_running,registorCount_stopped,running_standby_instanceItems,stopped_standby_instanceItems




def createEC2_Emergency(userId,zone,NewFastLaunchEC2Amount,appIds,eventId,eventTime):
    logger.info("======== createEC2_Emergency==============")
    lambdaclient = boto3.client('lambda')
    payload = { 
    "pathParameters": { "userid":userId},
    "body":
        { 
            "ec2zone":zone,
            "ec2type":"t3.medium",
            'userAMI':"withSteam",
            'spot':False,
            'amount':NewFastLaunchEC2Amount,
            'appids':appIds,
            'eventId':eventId,
            'eventTime':eventTime,
        } } 

    lambdaclient.invoke(FunctionName='Function_vbs_create_ec2_emergency',
    InvocationType='RequestResponse',                                      
    Payload=json.dumps(payload))        

def processEvent_User_AttachEC2_Emergency(userId,zone,NewFastLaunchEC2Amount,appIds,registeredInstances_Running,registeredInstances_Stopped,msgId,dateTimeStr,table,lambdaclient):
    
    logger.info("======== processEvent_User_AttachEC2_Emergency ------")
    createEC2_Emergency(userId,zone,NewFastLaunchEC2Amount,appIds,msgId,dateTimeStr)
    
    
    for item in registeredInstances_Running:
        eventRecord(table,item['instanceId']['S'],item['region']['S'],msgId,dateTimeStr,userId)
    for item in registeredInstances_Stopped:
        eventRecord(table,item['instanceId']['S'],item['region']['S'],msgId,dateTimeStr,userId)
    
    region=zone
    
    ec2ids,ec2regions=processPoolItemsToAPIFormat(registeredInstances_Stopped,len(registeredInstances_Stopped))
        
    startEC2(lambdaclient,ec2ids,ec2regions)

    attach_EBS_Volume(registeredInstances_Running,appIds,region)
    attach_EBS_Volume(registeredInstances_Stopped,appIds,region)
    sendEvent_Enlarge_Running_Pool(zone)
        

def processEvent_Enlarge_Stopped_Pool(message):
    logger.info("======== processEvent_Enlarge_Stopped_Pool ------")

    # action_event = message.message_attributes.get('ActionEvent').get('StringValue')
    lambdaclient=boto3.client('lambda')

    # body_json=json.loads(message.body)
    body_json=json.loads(message["body"])


    # logger.info(action_event)
    # logger.info(body_json)
    dateTimeStr = body_json['dateTimeStr']
    userId = body_json['userId']
    msgId = body_json['eventUUID']
    zone=body_json['zone']
    runningNum,stoppedNum,runningPoolItems,stoppedPoolItems=calculatePoolAmount(zone)
    logger.info("======== runningNum ------")
    logger.info(runningNum)
    logger.info("======== stoppedNum ------")
    logger.info(stoppedNum)

    if stoppedNum<stoppedThreshold:
        if runningNum>=runningThreshold:
            if runningNum-runningThreshold>=stoppedNum-stoppedThreshold:
                stoppedNum=abs(stoppedNum-stoppedThreshold)
                logger.info("======== processEvent_Enlarge_Stopped_Pool -- StopEC2+sendEvent_Shrink_Running_Pool ------")
                logger.info(stoppedNum)
                ec2ids,ec2regions=processPoolItemsToAPIFormat(stoppedPoolItems,stoppedNum)
                
                stopEC2(lambdaclient,ec2ids,ec2regions)
                sendEvent_Shrink_Running_Pool(zone)
            else:
                stoppingNum=abs(runningNum-runningThreshold)
                logger.info("======== processEvent_Enlarge_Stopped_Pool -- StopEC2+CreateEC2+sendEvent_Shrink_Running_Pool ------")
                
                ec2ids,ec2regions=processPoolItemsToAPIFormat(runningPoolItems,stoppingNum)
                createEC2Number=-stoppedNum+stoppedThreshold-stoppedNum

                createEC2(lambdaclient,zone,createEC2Number,userId,dateTimeStr,msgId)
                stopEC2(lambdaclient,ec2ids,ec2regions)

                sendEvent_Shrink_Running_Pool(zone)
            
        
        else:
            createEC2Number=-stoppedNum+stoppedThreshold-runningNum+runningThreshold
            logger.info("======== processEvent_Enlarge_Stopped_Pool --createEC2+sendEvent_Enlarge_Running_Pool ------")
            logger.info(createEC2Number)
            createEC2(lambdaclient,zone,createEC2Number,userId,dateTimeStr,msgId)
            sendEvent_Enlarge_Running_Pool(zone)
    else:
        checkProcessEventStatus(zone)


def startEC2(lambdaclient,ec2ids,ec2regions):
    payload = { 
        "pathParameters": { "userid":"HTC_RRTeam",'actionid':'start'},
        "body":
            { 
                'ec2ids':ec2ids,
                'ec2regions':ec2regions
            } 
    } 
    result = lambdaclient.invoke(FunctionName='Function_vbs_manage_ec2',
                InvocationType='RequestResponse',                                      
                Payload=json.dumps(payload))


def deleteEC2(lambdaclient,ec2ids,ec2regions):
    payload = { 
        "pathParameters": { "userid":"HTC_RRTeam",'actionid':'delete'},
        "body":
            { 
                'ec2ids':ec2ids,
                'ec2regions':ec2regions
            } 
    } 
    result = lambdaclient.invoke(FunctionName='Function_vbs_manage_ec2',
                InvocationType='RequestResponse',                                      
                Payload=json.dumps(payload))


def stopEC2(lambdaclient,ec2ids,ec2regions):

  
    payload = { 
        "pathParameters": { "userid":"HTC_RRTeam",'actionid':'stop'},
        "body":
            { 
                'ec2ids':ec2ids,
                'ec2regions':ec2regions
            } 
    } 
    result = lambdaclient.invoke(FunctionName='Function_vbs_manage_ec2',
                InvocationType='RequestResponse',                                      
                Payload=json.dumps(payload))

def createEC2(lambdaclient,zone,amount,userId,dateTimeStr,msgId):
    payload = { 
        "pathParameters": { "userid":"HTC_RRTeam"},
        "body":
            { 
                "ec2zone":zone,
                "ec2type":"t3.medium",
                'userAMI':"withSteam",
                'spot':False,
                'amount':amount,
                'appids':[],
                'eventId':msgId,
                'eventTime':dateTimeStr,

            } } 

    result = lambdaclient.invoke(FunctionName='Function_vbs_create_ec2',
                InvocationType='RequestResponse',                                      
                Payload=json.dumps(payload))

def processPoolItemsToAPIFormat(items,amount):
    ec2ids=[]
    ec2regions=[]
    count=0
    for item in items:
        region=item['region']['S']
        instanceId=item['instanceId']['S']
        ec2ids.append(instanceId)
        ec2regions.append(region)
        count=count+1
        if count==amount:
            break
    return ec2ids,ec2regions

def checkProcessEventStatus(zone):
    # Actions=[]
    runningNum,stoppedNum,runningPoolItems,stoppedPoolItems=calculatePoolAmount(zone)
    if runningNum==runningThreshold:
        logger.info("======== Running_Pool Good------")
    else:
        if runningNum>runningThreshold:
            # Actions.append('Shrink_Running_Pool')
            sendEvent_Shrink_Running_Pool(zone)
        else:
            # Actions.append('Enlarge_Running_Pool')
            sendEvent_Enlarge_Running_Pool(zone)
    
    if stoppedNum==stoppedThreshold:
        logger.info("======== Stopped_Pool Good------")
        if stoppedNum>stoppedThreshold:
            # Actions.append('Shrink_Stopped_Pool')
            sendEvent_Shrink_Stopped_Pool(zone)
        else:
            # Actions.append('Enlarge_Stopped_Pool')
            sendEvent_Enlarge_Stopped_Pool(zone)
        
        
def processEvent_Enlarge_Running_Pool(message):
    sqs = boto3.resource('sqs')
    queue = sqs.get_queue_by_name(QueueName='VBS_Cloud_MessageQueue')
    logger.info("======== processEvent_Enlarge_Running_Pool ------")

    # action_event = message.message_attributes.get('ActionEvent').get('StringValue')
    
    # body_json=json.loads(message.body)
    body_json=json.loads(message["body"])
    

    dateTimeStr = body_json['dateTimeStr']
    userId = body_json['userId']
    msgId = body_json['eventUUID']
    zone=body_json['zone']
    
    #####################query Pool Instance############
    runningNum,stoppedNum,runningPoolItems,stoppedPoolItems=calculatePoolAmount(body_json['zone'])
    lambdaclient = boto3.client('lambda')
    diff_running=runningNum-runningThreshold   
    diff_stopped=stoppedNum-stoppedThreshold

    logger.info("======== Pool Statics ------")
    logger.info("===running :")
    logger.info(runningNum)
    logger.info(runningThreshold)
    logger.info("===stopped :")
    logger.info(stoppedNum)
    logger.info(stoppedThreshold)
    if diff_running<0:   
        ###lack of running
        if diff_stopped>0:
            ### stopped ok
            if abs(diff_stopped)-abs(diff_running)<0:
                ###多的stopped 不夠補
                logger.info("startEC2()+createEC2()")
                
                ec2ids,ec2regions=processPoolItemsToAPIFormat(stoppedPoolItems,abs(diff_stopped))

                startEC2(lambdaclient,ec2ids,ec2regions)
                amount_newLaunch=abs(abs(diff_stopped)-abs(diff_running))
                createEC2(lambdaclient,body_json['zone'],amount_newLaunch,userId,dateTimeStr,msgId)

            else:#### 
                ####多的stopped 夠補
                logger.info("startEC2()")
                ec2ids,ec2regions=processPoolItemsToAPIFormat(stoppedPoolItems,abs(diff_running))

                startEC2(lambdaclient,ec2ids,ec2regions)
                  
        else:
            logger.info("createEC2() send Enlarge_Stopped_Pool")
            ### lack of stopped

            # createEC2(abs(diff_running)+abs(diff_stopped))
            # stope(abs(diff_stopped)) 
            # for i in range(abs(diff_running)+abs(diff_stopped)):
            #     createEC2(lambdaclient,body_json['zone'],1)
            amount_newLaunch=abs(diff_running)+abs(diff_stopped)
            createEC2(lambdaclient,body_json['zone'],amount_newLaunch,userId,dateTimeStr,msgId)
    
            ###send Enlarge_Stopped_Pool
            sendEvent_Enlarge_Stopped_Pool(body_json['zone'])
            # now_datetime = datetime.datetime.now()
            # dateTimeStr_new = now_datetime.strftime("%Y-%m-%d/%H:%M:%S:%f")
            
            # msgId_new=str(uuid.uuid4())
            # parameter = {"zone" : body_json['zone'],'dateTimeStr':dateTimeStr_new,'userId':'HTC_RRTeam','eventUUID':msgId_new}
            # parameterStr = json.dumps(parameter)
            
            # logger.info("======== parameterStr ------")
            # logger.info(parameterStr)
            # queue.send_message(
            #     MessageBody=parameterStr, 
            #     MessageAttributes={
            #     'ActionEvent': {
            #         'StringValue': 'Enlarge_Stopped_Pool',
            #         'DataType': 'String'
            #         },
            #     })
    else:
        checkProcessEventStatus(zone)
    

            


def messageProcess(action_event,message):
    if action_event=='AttachEC2':
        processEvent_attachEC2(message)
    elif action_event=='DetachEC2':
        processEvent_detachEC2(message)
    elif action_event=='Enlarge_Running_Pool':
        processEvent_Enlarge_Running_Pool(message)
    elif action_event=='Enlarge_Stopped_Pool':
        processEvent_Enlarge_Stopped_Pool(message)
    elif action_event=='Shrink_Running_Pool':
        processEvent_Shrink_Running_Pool(message)
    elif action_event=='Shrink_Stopped_Pool':
        processEvent_Shrink_Stopped_Pool(message)



def directlyProcess(event):
    logger.info("=================New Directly Process========")
    logger.info(len(event['Records']))
    processedRecord=None
    for record in event['Records']:
        logger.info("=================record========")
        logger.info(record)
        
        messageProcess(record['messageAttributes']['ActionEvent']['stringValue'],record)
        processedRecord=record
        break

    sqs_Resource = boto3.resource('sqs')
    queue = sqs_Resource.get_queue_by_name(QueueName='VBS_Cloud_MessageQueue_L1')
    for message in queue.receive_messages(MessageAttributeNames=['ActionEvent']):
        # action_event = message.message_attributes.get('ActionEvent').get('StringValue')
        logger.info("=================check queueMessage========")
        logger.info(message)
        logger.info("=================queueMessage:message.message_attributes========")
        logger.info(message.message_attributes)
        body_json=json.loads(message["body"])
        msgId = body_json['eventUUID']

        body_json2=json.loads(processedRecord["body"])
        msgId2 = body_json2['eventUUID']
        if msgId==msgId2:
            message.delete()
            


    
def queueProcess(queue):
    logger.info("=================queue========")
    logger.info(queue)
    for message in queue.receive_messages(MessageAttributeNames=['ActionEvent']):
    # for message in queue.receive_messages():
        
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
    
    consumingType='SimpleQueue'
    if consumingType=='SimpleQueue':

        directlyProcess(event)

    else:
        ###################### write event Log #######################
        queue_L1 = sqs_Resource.get_queue_by_name(QueueName='VBS_Cloud_MessageQueue_L1')
        queue_L2 = sqs_Resource.get_queue_by_name(QueueName='VBS_Cloud_MessageQueue_L2')
        queue_L3 = sqs_Resource.get_queue_by_name(QueueName='VBS_Cloud_MessageQueue_L3')
        Level1_Events=['AttachEC2','DetachEC2','Enlarge_Running_Pool']
        Level2_Events=['Enlarge_Stopped_Pool','Shrink_Running_Pool']
        Level3_Events=['Shrink_Stopped_Pool']
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
        
            queue.send_message(
                MessageBody=record['body'], 
                MessageAttributes={
                'ActionEvent': {
                    'StringValue': record['messageAttributes']['ActionEvent']['stringValue'],
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
    