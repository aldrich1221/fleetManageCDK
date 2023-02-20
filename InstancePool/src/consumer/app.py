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

import csv
import datetime

from os import environ
import collections
import time
import sys
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
  logger.info("========getSnapshotID response ------")
  logger.info(resp_dict)
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
    logger.info("======================================Now user write eventRecord ---------------------------------------")
    logger.info("start................................... ")
    
    
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
    
    logger.info(instanceId)
    logger.info(msgId)
    logger.info(datetime.datetime.now())        
    logger.info("................................... End")

def detach_EBS_Volume(instanceIds,regions):




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
    
    allVols=[]
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
            allVols.append({'vol_id':vol['vol_id'],'volume':volume})
    
    for item in allVols:
        try:

            waiter = ec2.get_waiter('volume_available')
            waiter.wait(VolumeIds=[item['vol_id']],)
            print (" INFO : Volume Detached")

            # Deleting Volume Device details already available
            item['volume'].delete()
        except:
            logger.info("can't delete vol")
           
def attach_EBS_Volume(finalInstances,appIds,region):
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
           
            ec2 = boto3.client('ec2')
       
        
            volsss = get_vol(iId, ec2)
            # print(volsss)
            alreadyHave=[]
            for vol in volsss:
                alreadyHave.append(vol['vol_device'])
            
            newdeviceName=list(set(deviceName)-set(alreadyHave))

            waiter = ec2.get_waiter('volume_available')
        
            waiter.wait(VolumeIds=[response['VolumeId']],)
            # print (" INFO : Volume Detached")

            response= ec2.attach_volume(Device=newdeviceName[blocki], InstanceId=instance_dict[iId][0], VolumeId=response['VolumeId'])
            # print("State : ",response['State'])


        blocki=blocki+1
    
def processEvent_Shrink_Running_Pool(message):

    logger.info("================processEvent_Shrink_Running_Pool----------------")
    
    dynamodbClient = boto3.client('dynamodb',region_name='us-east-1')
    dynamodb_resource = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb_resource.Table('VBS_Instance_Pool')
    
    lambdaclient=boto3.client('lambda',region_name='us-east-1')
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
    processCount=body_json['processCount']
    logger.info("================processCount----------------")
    logger.info(processCount)
    if processCount>5:
        return
    runningNum,stoppedNum,runningPoolItems,stoppedPoolItems=calculatePoolAmount(zone)
    logger.info("======== runningNum ------")
    logger.info(runningNum)
    logger.info("======== stoppedNum ------")
    logger.info(stoppedNum)
    if runningNum>runningThreshold: 
        if stoppedNum>=stoppedThreshold:
            logger.info("delete!+sendEvent_Shrink_Stopped_Pool")
            ec2ids,ec2regions=processPoolItemsToAPIFormat(runningPoolItems,runningNum-runningThreshold,msgId,dynamodbClient,table)
            deleteEC2(lambdaclient,ec2ids,ec2regions,msgId)
            
            # sendEvent_Shrink_Stopped_Pool(zone)
            checkProcessEventStatus(zone,processCount)

        elif stoppedNum<stoppedThreshold:
            logger.info("stopped! +sendEvent_Enlarge_Stopped_Pool")
            # ##To Stop
            # total=runningNum-runningThreshold
            # stopNum=total-(stoppedThreshold-stoppedNum)
            # deleteNum=total-stopNum
            # ec2ids,ec2regions=processPoolItemsToAPIFormat(runningPoolItems[:stopNum],stopNum)
            # stopEC2(lambdaclient,ec2ids,ec2regions)

            # ec2ids,ec2regions=processPoolItemsToAPIFormat(runningPoolItems[stopNum:],deleteNum)
            # deleteEC2(lambdaclient,ec2ids,ec2regions)
            ec2ids,ec2regions=processPoolItemsToAPIFormat(runningPoolItems,runningNum-runningThreshold,msgId,dynamodbClient,table)
            stopEC2(lambdaclient,ec2ids,ec2regions,msgId)

            # sendEvent_Enlarge_Stopped_Pool(zone)
            checkProcessEventStatus(zone,processCount)

    else:
        checkProcessEventStatus(zone,processCount)

def processEvent_Shrink_Stopped_Pool(message):
    logger.info("================processEvent_Shrink_Stopped_Pool----------------")
    lambdaclient=boto3.client('lambda',region_name='us-east-1')
    # action_event = message.message_attributes.get('ActionEvent').get('StringValue')
    # dateTimeStr = message.message_attributes.get('DateTime').get('StringValue')
    # userId = message.message_attributes.get('User').get('StringValue')
    # msgId = message.message_attributes.get('EventUUID').get('StringValue')
    # body_json=json.loads(message.body)
    body_json=json.loads(message["body"])
    
    dynamodbClient = boto3.client('dynamodb',region_name='us-east-1')
    dynamodb_resource = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb_resource.Table('VBS_Instance_Pool')
    
    logger.info(body_json)
    dateTimeStr = body_json['dateTimeStr']
    userId = body_json['userId']
    msgId = body_json['eventUUID']
    zone=body_json['zone']
    processCount=body_json['processCount']
    logger.info("================processCount----------------")
    logger.info(processCount)
    if processCount>5:
        return

    runningNum,stoppedNum,runningPoolItems,stoppedPoolItems=calculatePoolAmount(zone)
    logger.info("======== runningNum ------")
    logger.info(runningNum)
    logger.info("======== stoppedNum ------")
    logger.info(stoppedNum)
    if stoppedNum>stoppedThreshold:
        if runningNum<runningThreshold:
            if stoppedNum-stoppedThreshold>runningThreshold-runningNum:
                ##send
                ec2ids,ec2regions=processPoolItemsToAPIFormat(stoppedPoolItems,runningThreshold-runningNum,msgId,dynamodbClient,table)
                startEC2(lambdaclient,ec2ids,ec2regions,msgId)

                deleteNumber=stoppedNum-stoppedThreshold-(runningThreshold-runningNum)
                ec2ids,ec2regions=processPoolItemsToAPIFormat(stoppedPoolItems,runningThreshold-runningNum,msgId,dynamodbClient,table)
                deleteEC2(lambdaclient,ec2ids,ec2regions,msgId)

                checkProcessEventStatus(zone,processCount)

            else:
                ec2ids,ec2regions=processPoolItemsToAPIFormat(stoppedPoolItems,stoppedNum-stoppedThreshold,msgId,dynamodbClient,table)
                startEC2(lambdaclient,ec2ids,ec2regions,msgId)

                # sendEvent_Enlarge_Running_Pool(zone)
                checkProcessEventStatus(zone,processCount)


        else:
            
            ec2ids,ec2regions=processPoolItemsToAPIFormat(stoppedPoolItems,stoppedNum-stoppedThreshold,msgId,dynamodbClient,table)
            deleteEC2(lambdaclient,ec2ids,ec2regions,msgId)
            # sendEvent_Shrink_Running_Pool(zone)
            checkProcessEventStatus(zone,processCount)

    else:
        checkProcessEventStatus(zone,processCount)


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
    processCount=body_json['processCount']
    logger.info("================processCount----------------")
    logger.info(processCount)
    region=''
    send_Enlarge_Running_Pool=False
    send_Enlarge_Stopped_Pool=False

    dynamodbClient = boto3.client('dynamodb',region_name='us-east-1')
    lambdaclient=boto3.client('lambda',region_name='us-east-1')
   
    runningNum,stoppedNum,runningPoolItems,stoppedPoolItems=calculatePoolAmount(zone)
    logger.info("======== runningNum ------")
    logger.info(runningNum)
    logger.info("======== stoppedNum ------")
    logger.info(stoppedNum)
    
    
    ################ query the pool info and claim ownership##########################
    
    dynamodb_resource = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb_resource.Table('VBS_Instance_Pool')


    ###############with event lock############################
    registorCount_running=0
    registorCount_stopped=0
    registeredInstances_Running=[]
    registeredInstances_Stopped=[]
    for item in runningPoolItems:
        
        if getLockDataWrite(dynamodbClient,item['instanceId']['S'],msgId):
            lockDataWrite(item['instanceId']['S'],item['region']['S'],msgId,table)
            registorCount_running=registorCount_running+1
            registeredInstances_Running.append(item)
            
    
        
    for item in stoppedPoolItems:
        
        if getLockDataWrite(dynamodbClient,item['instanceId']['S'],msgId):
            lockDataWrite(item['instanceId']['S'],item['region']['S'],msgId,table)
            registorCount_stopped=registorCount_stopped+1
            registeredInstances_Stopped.append(item)

    

    ###############without event lock############################
    # registorCount_running=runningNum
    # registorCount_stopped=stoppedNum

    # registeredInstances_Running=runningPoolItems
    # registeredInstances_Stopped=stoppedPoolItems
    
 
   
    finalInstances=[]
    if registorCount_running+registorCount_stopped<amount:
        
        #################Emergency no need to unlock 
        logger.info("======== attach Emergency ------")
        logger.info(amount)
        logger.info("vs")
        logger.info(registorCount_running)
        logger.info(registorCount_stopped)
        NewFastLaunchEC2Amount=amount-(registorCount_running+registorCount_stopped)

        processEvent_User_AttachEC2_Emergency(userId,zone,NewFastLaunchEC2Amount,appIds,registeredInstances_Running,registeredInstances_Stopped,msgId,dateTimeStr,table,lambdaclient,processCount)
        
        # checkProcessEventStatus(zone)
        ###send Emergency
    else:
        alreadyAssignAmount=amount
        for item in registeredInstances_Running:
            if alreadyAssignAmount>0:
                # startEC2ByUser(lambdaclient,item['userId']['S'],item['instanceId']['S'],item['region']['S'])
        
                eventRecord(table,item['instanceId']['S'],item['region']['S'],msgId,dateTimeStr,userId)
                finalInstances.append(item)
                region=item['region']['S']
                alreadyAssignAmount=alreadyAssignAmount-1
                
            #####將不需要的Instance row unlock
            else:
                unLockDataWrite(item['instanceId']['S'],item['region']['S'],table)
            ##########without lock
            # if alreadyAssignAmount==0:
                #     break
               
            
        if alreadyAssignAmount>0:
            instancestartfromstopped=[]
            for item in registeredInstances_Stopped:
                region=item['region']['S']
                if alreadyAssignAmount>0:
                    # startEC2ByUser(lambdaclient,item['userId']['S'],item['instanceId']['S'],item['region']['S'])
                    eventRecord(table,item['instanceId']['S'],item['region']['S'],msgId,dateTimeStr,userId)
                    finalInstances.append(item)
                    instancestartfromstopped.append(item)
                    alreadyAssignAmount=alreadyAssignAmount-1
                
                #### with lock
                else:
                    unLockDataWrite(item['instanceId']['S'],item['region']['S'],table)
                # if alreadyAssignAmount==0:
                #     break
        else:
            for item in registeredInstances_Stopped:
                region=item['region']['S']
                unLockDataWrite(item['instanceId']['S'],item['region']['S'],table)
            
        ec2ids,ec2regions=processPoolItemsToAPIFormat(finalInstances,len(finalInstances),msgId,dynamodbClient,table)
    
        # startEC2(lambdaclient,ec2ids,ec2regions)
        startEC2ByUser(lambdaclient,userId,ec2ids,ec2regions,msgId,True)

        send_Enlarge_Running_Pool=True     
        attach_EBS_Volume(finalInstances,appIds,region)
    checkProcessEventStatus(zone,processCount)
        
        
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

    # sqs = boto3.resource('sqs',region_name='us-east-1')
    # queue = sqs.get_queue_by_name(QueueName='VBS_Cloud_MessageQueue')
    
    # ############### send Enlarge_Running_Pool###################
    # if send_Enlarge_Running_Pool==True:

    #     sendEvent_Enlarge_Running_Pool(zone)
        
    # ################ send Enlarge_Stopped_Pool###################
    # if send_Enlarge_Stopped_Pool==True:
    #     now_datetime = datetime.datetime.now()
    #     dateTimeStr_new = now_datetime.strftime("%Y-%m-%d/%H:%M:%S:%f")
        
    #     msgId_new=str(uuid.uuid4())
    #     parameter = {"zone" : zone,'dateTimeStr':dateTimeStr_new,'userId':'HTC_RRTeam','eventUUID':msgId_new}
    #     parameterStr = json.dumps(parameter)
        
    #     logger.info("======== parameterStr ------")
    #     logger.info(parameterStr)
    #     queue.send_message(
    #         MessageBody=parameterStr, 
    #         MessageAttributes={
    #         'ActionEvent': {
    #             'StringValue': 'Enlarge_Stopped_Pool',
    #             'DataType': 'String'
    #             },
    #         })


def sendEvent_Shrink_Running_Pool(zone,processCount):
    logger.info("======== sendEvent_Shrink_Running_Pool ------")
    
    # sqs = boto3.resource('sqs',region_name='us-east-1')
    
    
    # queue = sqs.get_queue_by_name(QueueName='VBS_Cloud_MessageQueue')
    client = boto3.client('sqs',region_name='us-east-1')
    response = client.get_queue_url(
    QueueName='VBS_Cloud_MessageQueue',
    # QueueOwnerAWSAccountId='string'

    )
    logger.info("======== response ------")
    logger.info(response)
    
    sqs = boto3.resource('sqs',region_name='us-east-1')
    queue = sqs.Queue(response['QueueUrl'])
    
    
    
    now_datetime = datetime.datetime.now()
    dateTimeStr_new = now_datetime.strftime("%Y-%m-%d/%H:%M:%S:%f")
    
    msgId_new=str(uuid.uuid4())
    parameter = {
        "zone" : zone,
        'dateTimeStr':dateTimeStr_new,
        'userId':'HTC_RRTeam',
        'eventUUID':msgId_new,
        'processCount':processCount+1
        }
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

def sendEvent_Shrink_Stopped_Pool(zone,processCount):
    # sqs = boto3.resource('sqs',region_name='us-east-1')
    # queue = sqs.get_queue_by_name(QueueName='VBS_Cloud_MessageQueue')
    
    logger.info("======== sendEvent_Shrink_Stopped_Pool ------")
    # logger.info(parameterStr)
    
    client = boto3.client('sqs',region_name='us-east-1')
    response = client.get_queue_url(
    QueueName='VBS_Cloud_MessageQueue',
    # QueueOwnerAWSAccountId='string'

    )
    sqs = boto3.resource('sqs',region_name='us-east-1')
    queue = sqs.Queue(response['QueueUrl'])
    
    
    now_datetime = datetime.datetime.now()
    dateTimeStr_new = now_datetime.strftime("%Y-%m-%d/%H:%M:%S:%f")
    
    msgId_new=str(uuid.uuid4())
    parameter = {"processCount":processCount+1,"zone" : zone,'dateTimeStr':dateTimeStr_new,'userId':'HTC_RRTeam','eventUUID':msgId_new}
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

def sendEvent_Enlarge_Stopped_Pool(zone,processCount):
    logger.info("======== sendEvent_Enlarge_Stopped_Pool ------")
    # sqs = boto3.resource('sqs',region_name='us-east-1')
    
    # queue = sqs.get_queue_by_name(QueueName='VBS_Cloud_MessageQueue')
    
    
    client = boto3.client('sqs',region_name='us-east-1')
    response = client.get_queue_url(
    QueueName='VBS_Cloud_MessageQueue',
    # QueueOwnerAWSAccountId='string'

    )
    sqs = boto3.resource('sqs',region_name='us-east-1')
    queue = sqs.Queue(response['QueueUrl'])
    
    
    now_datetime = datetime.datetime.now()
    dateTimeStr_new = now_datetime.strftime("%Y-%m-%d/%H:%M:%S:%f")
    
    msgId_new=str(uuid.uuid4())

    parameter = {"processCount":processCount+1,"zone" : zone,'dateTimeStr':dateTimeStr_new,'userId':'HTC_RRTeam','eventUUID':msgId_new}
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

def sendEvent_Enlarge_Running_Pool(zone,processCount):
    
    logger.info("========sendEvent_Enlarge_Running_Pool ------")
    # sqs = boto3.resource('sqs',region_name='us-east-1')
    # queue = sqs.get_queue_by_name(QueueName='VBS_Cloud_MessageQueue')
    
    client = boto3.client('sqs',region_name='us-east-1')
    response = client.get_queue_url(
    QueueName='VBS_Cloud_MessageQueue',
    # QueueOwnerAWSAccountId='string'

    )
    sqs = boto3.resource('sqs',region_name='us-east-1')
    queue = sqs.Queue(response['QueueUrl'])
    
    
    now_datetime = datetime.datetime.now()
    dateTimeStr_new = now_datetime.strftime("%Y-%m-%d/%H:%M:%S:%f")
    
    msgId_new=str(uuid.uuid4())

    parameter = {"processCount":processCount+1,"zone" : zone,'dateTimeStr':dateTimeStr_new,'userId':'HTC_RRTeam','eventUUID':msgId_new}
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
    processCount=body_json['processCount']
    logger.info("======== processEvent_detachEC2  msgId------")
    logger.info(msgId)
    logger.info("================processCount----------------")
    logger.info(processCount)
    dynamodbClient = boto3.client('dynamodb',region_name='us-east-1')
    dynamodb_resource = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb_resource.Table('VBS_Instance_Pool')


    ### usage and cost Compute
    usageCompute(instances_to_datach,regions,dynamodbClient,userId,msgId)  

    logger.info("======== processEvent_detachEC2 : detachEBS------")
    
    detach_EBS_Volume(instances_to_datach,regions)
    uniqueRegions=[]
    logger.info("======== processEvent_detachEC2::release ------")
    for i in range(len(instances_to_datach)):
        if regions[i] not in uniqueRegions:
            uniqueRegions.append(regions[i])
        
        releaseInstance(table,instances_to_datach[i],regions[i],msgId,dateTimeStr)
        unLockDataWrite(instances_to_datach[i],regions[i],table)
    
    logger.info("======== processEvent_detachEC2::check pool ------")
    for region in uniqueRegions:
        logger.info(region)
        checkProcessEventStatus(region,processCount)
        # sendEvent_Shrink_Running_Pool(region)


def calculatePoolAmount(zone):
    
    logger.info("========calculatePoolAmount ------")
    dynamodbClient = boto3.client('dynamodb',region_name='us-east-1')
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
    lambdaclient = boto3.client('lambda',region_name='us-east-1')
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
            'emergency':True
        } } 

    # response=lambdaclient.invoke(FunctionName='Function_vbs_create_ec2_emergency',
    # InvocationType='RequestResponse',                                      
    # Payload=json.dumps(payload))       
    # logger.info("======== createEC2_Emergency Response==============") 
    # logger.info(response)  
    response=lambdaclient.invoke(FunctionName='Function_vbs_create_ec2',
    InvocationType='RequestResponse',                                      
    Payload=json.dumps(payload))       
    logger.info("======== createEC2_Emergency Response==============") 
    logger.info(response)   
    
    return response

def processEvent_User_AttachEC2_Emergency(userId,zone,NewFastLaunchEC2Amount,appIds,registeredInstances_Running,registeredInstances_Stopped,msgId,dateTimeStr,table,lambdaclient,processCount):
    
    

    msgId_emergency=str(uuid.uuid4())
    logger.info("======== processEvent_User_AttachEC2_Emergency ------")
    logger.info("======== processEvent_User_AttachEC2_Emergency :createEC2_Emergency ------")
    logger.info("NewFastLaunchEC2Amount")
    logger.info(NewFastLaunchEC2Amount)
    response_createEC2=createEC2_Emergency(userId,zone,NewFastLaunchEC2Amount,appIds,msgId,dateTimeStr)
    logger.info(response_createEC2)
    dynamodbClient = boto3.client('dynamodb',region_name='us-east-1')
    dynamodb_resource = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb_resource.Table('VBS_Instance_Pool')
    
    
    for item in registeredInstances_Running:
        eventRecord(table,item['instanceId']['S'],item['region']['S'],msgId,dateTimeStr,userId)
    for item in registeredInstances_Stopped:
        eventRecord(table,item['instanceId']['S'],item['region']['S'],msgId,dateTimeStr,userId)
    
    region=zone
    
    logger.info("======== processEvent_User_AttachEC2_Emergency :startec2 ------")

    ec2ids,ec2regions=processPoolItemsToAPIFormat(registeredInstances_Stopped,len(registeredInstances_Stopped),msgId,dynamodbClient,table)    
    # startEC2(lambdaclient,ec2ids,ec2regions)
    startEC2ByUser(lambdaclient,userId,ec2ids,ec2regions,msgId,True)

    ec2ids,ec2regions=processPoolItemsToAPIFormat(registeredInstances_Running,len(registeredInstances_Running),msgId,dynamodbClient,table)    
    # startEC2(lambdaclient,ec2ids,ec2regions)
    startEC2ByUser(lambdaclient,userId,ec2ids,ec2regions,msgId,True)



    logger.info("======== processEvent_User_AttachEC2_Emergency :attachEBS ------")
    logger.info(registeredInstances_Running)
    
    attach_EBS_Volume(registeredInstances_Running,appIds,region)
    
    logger.info(registeredInstances_Stopped)
    attach_EBS_Volume(registeredInstances_Stopped,appIds,region)
    
    
    logger.info("======== processEvent_User_AttachEC2_Emergency :create new instance for stand-by ------")
    createEC2(lambdaclient,zone,stoppedThreshold+runningThreshold,'HTC_RRTeam',dateTimeStr,msgId_emergency)
    sendEvent_Enlarge_Running_Pool(zone,processCount)
        

def processEvent_Enlarge_Stopped_Pool(message):
    logger.info("======== processEvent_Enlarge_Stopped_Pool ------")

    # action_event = message.message_attributes.get('ActionEvent').get('StringValue')
    lambdaclient=boto3.client('lambda',region_name='us-east-1')

    dynamodbClient = boto3.client('dynamodb',region_name='us-east-1')
    dynamodb_resource = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb_resource.Table('VBS_Instance_Pool')
    
    # body_json=json.loads(message.body)
    body_json=json.loads(message["body"])


    # logger.info(action_event)
    # logger.info(body_json)
    dateTimeStr = body_json['dateTimeStr']
    userId = body_json['userId']
    msgId = body_json['eventUUID']
    zone=body_json['zone']
    processCount=body_json['processCount']

    logger.info("================processCount----------------")
    logger.info(processCount)
    if processCount>5:
        return
    runningNum,stoppedNum,runningPoolItems,stoppedPoolItems=calculatePoolAmount(zone)
    logger.info("======== runningNum ------")
    logger.info(runningNum)
    logger.info("======== stoppedNum ------")
    logger.info(stoppedNum)


    if stoppedNum<stoppedThreshold:
        if runningNum>runningThreshold:
            if abs(runningNum-runningThreshold)>abs(stoppedNum-stoppedThreshold):
                stoppedNum=abs(stoppedNum-stoppedThreshold)
                logger.info("======== processEvent_Enlarge_Stopped_Pool -- StopEC2+sendEvent_Shrink_Running_Pool ------")
                logger.info(stoppedNum)
                ec2ids,ec2regions=processPoolItemsToAPIFormat(stoppedPoolItems,stoppedNum,msgId,dynamodbClient,table)
                
                stopEC2(lambdaclient,ec2ids,ec2regions,msgId)
                # sendEvent_Shrink_Running_Pool(zone)

                checkProcessEventStatus(zone,processCount)

            else:
                stoppingNum=abs(runningNum-runningThreshold)
                logger.info("======== processEvent_Enlarge_Stopped_Pool -- StopEC2+CreateEC2+sendEvent_Shrink_Running_Pool ------")
                
                ec2ids,ec2regions=processPoolItemsToAPIFormat(runningPoolItems,stoppingNum,msgId,dynamodbClient,table)
                createEC2Number=-stoppedNum+stoppedThreshold-stoppedNum

                createEC2(lambdaclient,zone,createEC2Number,"HTC_RRTeam",dateTimeStr,msgId)
                stopEC2(lambdaclient,ec2ids,ec2regions,msgId)

                # sendEvent_Shrink_Running_Pool(zone)
                checkProcessEventStatus(zone,processCount)

            
        
        else:
            createEC2Number=-stoppedNum+stoppedThreshold-runningNum+runningThreshold
            logger.info("======== processEvent_Enlarge_Stopped_Pool --createEC2+sendEvent_Enlarge_Running_Pool ------")
            logger.info(createEC2Number)
            createEC2(lambdaclient,zone,createEC2Number,"HTC_RRTeam",dateTimeStr,msgId)
            # sendEvent_Enlarge_Running_Pool(zone)
            checkProcessEventStatus(zone,processCount)

    else:
        checkProcessEventStatus(zone,processCount)



def startEC2(lambdaclient,ec2ids,ec2regions,eventId):
    payload = { 
        "pathParameters": { "userid":"HTC_RRTeam",'actionid':'start'},
        "body":
            { 
                'ec2ids':ec2ids,
                'ec2regions':ec2regions,
                'eventId':eventId,
                'byUser':False
            } 
    } 
    lambdaclient.invoke(FunctionName='Function_vbs_manage_ec2',
                InvocationType='RequestResponse',                                      
                Payload=json.dumps(payload))


def lockDataWrite(instanceId,region,eventId,dbtable):
    logger.info(eventId)
    response = dbtable.update_item(
                Key={
                    'instanceId':instanceId,
                    'region':region
                },
                UpdateExpression="set eventLock = :a",
                ExpressionAttributeValues={
                    ':a': eventId,  
                },
                ReturnValues="UPDATED_NEW"
            )
            
    

def unLockDataWrite(instanceId,region,dbtable):
    
    response = dbtable.update_item(
                Key={
                    'instanceId':instanceId,
                    'region':region
                },
                UpdateExpression="set eventLock = :a",
                ExpressionAttributeValues={
                    ':a': '',  
                },
                ReturnValues="UPDATED_NEW"
            )

def getLockDataWrite(dynamodbClient,instancesId,eventId):
    
    response =dynamodbClient.query(
    TableName='VBS_Instance_Pool',
    ReturnConsumedCapacity='INDEXES',
    ScanIndexForward=False, # return results in descending order of sort key
    KeyConditionExpression='instanceId = :z',
    ExpressionAttributeValues={":z": {"S": instancesId}}
    ) 

    logger.info("========  getLockDataWrite reponse------")
    logger.info(response)
    if (response['Items'][0]['eventLock']['S']=='')or(response['Items'][0]['eventLock']['S']==eventId):
        return True
    else:
        return False


def deleteEC2(lambdaclient,ec2ids,ec2regions,eventId):
    payload = { 
        "pathParameters": { "userid":"HTC_RRTeam",'actionid':'delete'},
        "body":
            { 
                'ec2ids':ec2ids,
                'ec2regions':ec2regions,
                'eventId':eventId,
            } 
    } 
    result = lambdaclient.invoke(FunctionName='Function_vbs_manage_ec2',
                InvocationType='RequestResponse',                                      
                Payload=json.dumps(payload))
    


def stopEC2(lambdaclient,ec2ids,ec2regions,eventId):
    dynamodbClient=boto3.client('dynamodb',region_name='us-east-1')
    finalRegion=[]
    finalIds=[]
    for i in range(len(ec2ids)):
        instancesId=ec2ids[i]
        response =dynamodbClient.query(
            TableName='VBS_Instance_Pool',
            ReturnConsumedCapacity='INDEXES',
            ScanIndexForward=False, # return results in descending order of sort key
            KeyConditionExpression='instanceId = :z',
            ExpressionAttributeValues={":z": {"S": instancesId}}
            ) 
        if response['Items'][0]['userId']['S']=='HTC_RRTeam':
            finalRegion.append(ec2regions[i])
            finalIds.append(ec2ids[i])

    payload = { 
        "pathParameters": { "userid":"HTC_RRTeam",'actionid':'stop'},
        "body":
            { 
                'ec2ids':finalIds,
                'ec2regions':finalRegion,
                 'eventId':eventId,
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
                'emergency':False

            } } 

    result = lambdaclient.invoke(FunctionName='Function_vbs_create_ec2',
                InvocationType='RequestResponse',                                      
                Payload=json.dumps(payload))

def processPoolItemsToAPIFormat(items,amount,msgId,dynamodbClient,table):
    ec2ids=[]
    ec2regions=[]
    count=0
    logger.info("================== Start processPoolItemsToAPIFormat ----------------------------")
    logger.info(msgId)
    
    for item in items:
        region=item['region']['S']
        instanceId=item['instanceId']['S']
        eventLock=item['eventLock']['S']
        logger.info("Each instanceId")
        logger.info(instanceId)
        logger.info(eventLock)
        if getLockDataWrite(dynamodbClient,instanceId,msgId):
            lockDataWrite(instanceId,region,msgId,table)
            ec2ids.append(instanceId)
            ec2regions.append(region)
            count=count+1
            if count==amount:
                break
    logger.info(ec2ids)
    logger.info("================== End processPoolItemsToAPIFormat ----------------------------")
    return ec2ids,ec2regions


def startEC2ByUser(lambdaclient,userId,ec2id,ec2region,eventId,byUser):
    logger.info("================== startEC2ByUser ----------------------------")
    logger.info(ec2id)
    logger.info(eventId)
    payload = { 
                        "pathParameters": { "userid":userId,'actionid':'start'},
                        "body":
                            { 
                                'ec2ids':ec2id,
                                'ec2regions':ec2region,
                                'eventId':eventId,
                                'byUser':byUser
                            } 
                    } 
    lambdaclient.invoke(FunctionName='Function_vbs_manage_ec2',
                InvocationType='RequestResponse',                                      
                Payload=json.dumps(payload))
def FixNoStartingIssueAfterAssignedToUser(zone):
    dynamodbClient = boto3.client('dynamodb',region_name='us-east-1')
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
    lambdaclient = boto3.client('lambda',region_name='us-east-1')
    for item in response['Items']:
        if (item['available']['S']=='true'):
           if ((item['userId']['S']!='HTC_RRTeam') & (item['userId']['S']!='')):
                if item['instanceStatus']['S']!='running':
                    startEC2ByUser(lambdaclient,item['userId']['S'],item['instanceId']['S'],item['region']['S'])
                   
 

        
def checkProcessEventStatus(zone,processCount):
    # Actions=[]
    logger.info("======== checkProcessEventStatus------")
    
    runningNum,stoppedNum,runningPoolItems,stoppedPoolItems=calculatePoolAmount(zone)
    # FixNoStartingIssueAfterAssignedToUser(zone)

    logger.info("======== runningNum ------")
    logger.info(runningNum)
    logger.info("======== stoppedNum ------")
    logger.info(stoppedNum)
    
    if runningNum==runningThreshold:
        logger.info("======== Running_Pool Good------")
    else:
        if runningNum>runningThreshold:
            # Actions.append('Shrink_Running_Pool')
            sendEvent_Shrink_Running_Pool(zone,processCount)
        elif runningNum<runningThreshold:
            # Actions.append('Enlarge_Running_Pool')
            sendEvent_Enlarge_Running_Pool(zone,processCount)
    
    if stoppedNum==stoppedThreshold:
        logger.info("======== Stopped_Pool Good------")
    else:
        if stoppedNum>stoppedThreshold:
            # Actions.append('Shrink_Stopped_Pool')
            sendEvent_Shrink_Stopped_Pool(zone,processCount)
        elif stoppedNum<stoppedThreshold:
            # Actions.append('Enlarge_Stopped_Pool')
            sendEvent_Enlarge_Stopped_Pool(zone,processCount)
        
        
def processEvent_Enlarge_Running_Pool(message):
    sqs = boto3.resource('sqs',region_name='us-east-1')
    queue = sqs.get_queue_by_name(QueueName='VBS_Cloud_MessageQueue')
    logger.info("======== processEvent_Enlarge_Running_Pool ------")

    # action_event = message.message_attributes.get('ActionEvent').get('StringValue')
    
    # body_json=json.loads(message.body)
    body_json=json.loads(message["body"])
    
    
    dynamodbClient = boto3.client('dynamodb',region_name='us-east-1')
    dynamodb_resource = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb_resource.Table('VBS_Instance_Pool')

    dateTimeStr = body_json['dateTimeStr']
    userId = body_json['userId']
    msgId = body_json['eventUUID']
    zone=body_json['zone']
    processCount=body_json['processCount']
    logger.info("================processCount----------------")
    logger.info(processCount)
    if processCount>5:
        return
    #####################query Pool Instance############
    runningNum,stoppedNum,runningPoolItems,stoppedPoolItems=calculatePoolAmount(body_json['zone'])
    
    logger.info("======== runningNum ------")
    logger.info(runningNum)
    logger.info("======== stoppedNum ------")
    logger.info(stoppedNum)
    
    
    lambdaclient = boto3.client('lambda',region_name='us-east-1')
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
                
                ec2ids,ec2regions=processPoolItemsToAPIFormat(stoppedPoolItems,abs(diff_stopped),msgId,dynamodbClient,table)

                startEC2(lambdaclient,ec2ids,ec2regions,msgId)
                amount_newLaunch=abs(abs(diff_stopped)-abs(diff_running))
                createEC2(lambdaclient,body_json['zone'],amount_newLaunch,userId,dateTimeStr,msgId)
                
                checkProcessEventStatus(zone,processCount)

            else:#### 
                ####多的stopped 夠補
                logger.info("startEC2()")
                ec2ids,ec2regions=processPoolItemsToAPIFormat(stoppedPoolItems,abs(diff_running),msgId,dynamodbClient,table)

                startEC2(lambdaclient,ec2ids,ec2regions,msgId)
                checkProcessEventStatus(zone,processCount)

                  
        else:
            logger.info("createEC2() send Enlarge_Stopped_Pool")
            ### lack of stopped

            # createEC2(abs(diff_running)+abs(diff_stopped))
            # stope(abs(diff_stopped)) 
            # for i in range(abs(diff_running)+abs(diff_stopped)):
            #     createEC2(lambdaclient,body_json['zone'],1)
            amount_newLaunch=abs(diff_running)+abs(diff_stopped)
            createEC2(lambdaclient,body_json['zone'],amount_newLaunch,"HTC_RRTeam",dateTimeStr,msgId)
    
            ###send Enlarge_Stopped_Pool
            # sendEvent_Enlarge_Stopped_Pool(body_json['zone'])
            checkProcessEventStatus(zone,processCount)





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
        checkProcessEventStatus(zone,processCount)
    

            


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

    sqs_Resource = boto3.resource('sqs',region_name='us-east-1')
    queue = sqs_Resource.get_queue_by_name(QueueName='VBS_Cloud_MessageQueue')
    for message in queue.receive_messages(MessageAttributeNames=['ActionEvent']):
        # action_event = message.message_attributes.get('ActionEvent').get('StringValue')
        logger.info("=================check queueMessage========")
        logger.info(message)
        logger.info("=================queueMessage:message.message_attributes========")
        logger.info(message.message_attributes)
        logger.info(message.body)
        logger.info(message.attributes)
        logger.info(message.message_id)
        logger.info(message.md5_of_message_attributes)
        logger.info("=================queueMessage:message[1body]========")
        logger.info(message.body)
        
        body_json=json.loads(message.body)
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
    sqs = boto3.client('sqs',region_name='us-east-1')
    sqs_Resource = boto3.resource('sqs',region_name='us-east-1')
    
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
    