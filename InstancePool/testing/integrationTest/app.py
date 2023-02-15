import re
import boto3
import json
import boto3
import logging
import boto3
import datetime
import uuid
import requests
import random
import time
AccessControlAllowOrigin="https://d1wzk0972nk23y.cloudfront.net"
logger = logging.getLogger()
logger.setLevel(logging.INFO)
class CustomError(Exception):
  pass
def call_attachEC2(userId,region,amount,appIds):
  baseUrl="https://uy56z0gnck.execute-api.us-east-1.amazonaws.com/prod/v1"
 
  headers = {
        'authorizationtoken':'Basic cnJ0ZWFtOmlsb3ZlaHRj',
        'accept': 'application/json' 
    }

  bodyData={"amount":amount,"appIds":appIds}
  
  logger.info("======== call_attachEC2 ------")
  logger.info(amount)
  logger.info(appIds)
  logger.info(userId)
  logger.info(region)
  
  logger.info("======== send call_attachEC2 ------")
  bodyData=json.dumps(bodyData)
  req = requests.post(
   baseUrl+"/user/"+userId+"/region/"+region,
   headers=headers,
  data=bodyData
    # json=bodyData
    )
  resp_dict = req.json()
  logger.info("======== call_attachEC2 response ------")
  logger.info(resp_dict)
  return resp_dict


def call_detachEC2(userId,regions,ec2ids):
  baseUrl="https://e6yl26f3el.execute-api.us-east-1.amazonaws.com/prod/v1"
 

  headers = {
        'authorizationtoken':'Basic cnJ0ZWFtOmlsb3ZlaHRj',
        'accept': 'application/json' 
    }

      
  bodyData={"instanceIds":ec2ids,"regionids":regions}
  bodyData=json.dumps(bodyData)
  
  logger.info("======== call_detachEC2 ------")
  logger.info(len(ec2ids))
  logger.info(ec2ids)
  
  req = requests.post(
   baseUrl+"/user/"+userId,
   headers=headers,
   data=bodyData
    )
  resp_dict = req.json()
  logger.info("======== call_detachEC2 response ------")
  logger.info(resp_dict)
  return resp_dict
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
def queryInstanceByEventId(eventId,userId,amount):
    ################### waiting for ownership############ 
    availableInstances=[]
    whileCount=0
    import time
    lambdaclient=boto3.client('lambda',region_name='us-east-1')
    while(True):
        time.sleep(1)
        dynamodbClient = boto3.client('dynamodb',region_name='us-east-1')
        response =dynamodbClient.query(
        TableName='VBS_Instance_Pool',
        IndexName="eventId-index",
        Select='ALL_PROJECTED_ATTRIBUTES',
        # ConsistentRead=True,
        ReturnConsumedCapacity='INDEXES',
        ScanIndexForward=False, # return results in descending order of sort key
        KeyConditionExpression='eventId = :z',
        ExpressionAttributeValues={":z": {"S": eventId}}
        )   
        # logger.info("======== response ------")
        # logger.info(response)
        availableInstanceCount=0
        availableInstances=[]
        for item in response['Items']:
            if (item['available']['S']=='true') & (item['userId']['S']==userId) & (item['eventId']['S']==eventId):
                newItem={
                    'instanceId':item['instanceId']['S'],
                    'instanceIp':item['instanceIp']['S'],
                    'available':item['available']['S'],
                    'userId':item['userId']['S'],
                    'eventId':item['eventId']['S'],
                    'zone':item['zone']['S'],
                    'region':item['region']['S']
                }
                logger.info("availableInstanceCount")
                logger.info(availableInstanceCount)
                logger.info("request amount")
                logger.info(amount)
                
                # if item['instanceIp']['S']!='':
                #     availableInstances.append(newItem)
                #     availableInstanceCount=availableInstanceCount+1
                    
                if item['instanceIp']['S']!='':
                    availableInstances.append(newItem)
                    availableInstanceCount=availableInstanceCount+1
                else:
                    
                    startEC2(lambdaclient,[item['instanceId']['S']],[item['region']['S']],userId)
        if availableInstanceCount==amount:
            break
        whileCount=whileCount+1
        if whileCount>200:
            break
    
    dynamodb_resource = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb_resource.Table('VBS_Instance_Pool')
    regions=[]
    ids=[]
    ips=[]
    for item in availableInstances:
        regions.append(item['zone'])
        ids.append(item['instanceId'])
        ips.append(item['instanceIp'])
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
    logger.info("======== availableInstances-------------")
    logger.info(availableInstances)
    return ids,regions,ips
    
def processPoolItemsToAPIFormat(response,amount):
    ec2ids=[]
    ec2regions=[]
    ec2ips=[]
    count=0
    eventId=''
    if response[0]['data']['processingStatus']=='done':
        items=response[0]['data']['data']
        
        for item in items:
            region=item['zone']
            instanceId=item['instanceId']
            eventId=item['eventId']
            ec2ids.append(instanceId)
            ec2regions.append(region)
            ec2ips.append(item['instanceIp'])        
    
    else:
         
        item=response[0]['data']['data']
        eventId=item['eventUUID']
        userId=item['userId']
        ec2ids,ec2regions,ec2ips=queryInstanceByEventId(eventId,userId,amount)
    
    logger.info("Final------------- Get Instance Info: ")
    logger.info("evnetId / ec2ids /ec2ips")
    logger.info(eventId)
    
    logger.info(ec2ids)
    logger.info(ec2ips)
    logger.info("Final-------------Done ")
    
    
    return ec2ids,ec2regions
        

def integrationTest_singleRegion_random(regionId,body):
    tries=body['tries']
    maxInstancesPerReq=body['maxInstancesPerReq']

    userId="integrationtest"
    appIds=[
        "bbee173e-955c-4f3d-a0b9-b37f45502dc2",
        "f16e6a8c-4091-4453-a1c7-1cbc6814d9c4"
        ]

    logger.info("======== integrationTest_singleRegion_random------")
 
    trycount=tries
    allRequestInstanceNums=[]
    for i in range(tries):
        allRequestInstanceNums.append(random.randint(1,maxInstancesPerReq))

    allRequestInstanceNums_toAttach=allRequestInstanceNums
    allRequestInstanceNums_toDetach=allRequestInstanceNums

    

    random.shuffle(allRequestInstanceNums_toAttach)
    random.shuffle(allRequestInstanceNums_toDetach)


    # ####
    # allRequestInstanceNums_toAttach=[1,2,3]
    # allRequestInstanceNums_toDetach=[2,2,2]

    nowTotalInUse=0
    attachIndex=0
    detachIndex=0
    AllEC2Ids=[]
    AllEC2Regions=[]

    AttachWaitingTime=[]
    total=0
    whilecount=0
    while (len(allRequestInstanceNums_toAttach)>0) or (len(allRequestInstanceNums_toDetach)>0):
        
        if random.random()>0.5:
            logger.info("Go attach......")
            logger.info("======================================= whilecount ---------------------------")
            logger.info(whilecount)
            if len(allRequestInstanceNums_toAttach)>0:
              
                attachAmount=allRequestInstanceNums_toAttach.pop()
                nowTotalInUse=nowTotalInUse+attachAmount
                
                start_datetime = datetime.datetime.now()
                reponse=call_attachEC2(userId,regionId,attachAmount,appIds)
                ec2ids,ec2regions=processPoolItemsToAPIFormat(reponse,attachAmount)
                end_datetime = datetime.datetime.now()
                diff=end_datetime-start_datetime
                diff_totalseconds=diff.total_seconds()
                AttachWaitingTime.append(float(diff_totalseconds))        
                logger.info("Attach Time: ")
                logger.info(diff_totalseconds)
                total=total+float(diff_totalseconds)     
                AllEC2Ids=AllEC2Ids+ec2ids
                AllEC2Regions=AllEC2Regions+ec2regions
                logger.info(reponse)
        else:
            logger.info("Go detach......")
            logger.info("======================================= whilecount ---------------------------")
            logger.info(whilecount)
            if len(allRequestInstanceNums_toDetach)>0:
                detachAmount=allRequestInstanceNums_toDetach.pop()
                logger.info("detachAmount")
                logger.info(detachAmount)
                logger.info(nowTotalInUse)
                if nowTotalInUse<detachAmount:
                    # attachAmount=allRequestInstanceNums_toAttach.pop()
                    # logger.info(attachAmount)
                    allRequestInstanceNums_toDetach.append(detachAmount)
    
                    
                    # nowTotalInUse=nowTotalInUse+attachAmount
                    
                    
                    
                    # start_datetime = datetime.datetime.now()
                    # reponse=call_attachEC2(userId,regionId,attachAmount,appIds)
                    # ec2ids,ec2regions=processPoolItemsToAPIFormat(reponse)
                    # end_datetime = datetime.datetime.now()
                    # diff=end_datetime-start_datetime
                    # diff_totalseconds=diff.total_seconds()
                    # total=total+float(diff_totalseconds)   
                    # AttachWaitingTime.append(float(diff_totalseconds))        
                    # logger.info("Attach Time: ")
                    # logger.info(diff_totalseconds)
                    
                    
                    # logger.info(reponse)
                    
                    
                    
                    
                    # AllEC2Ids=AllEC2Ids+ec2ids
                    # AllEC2Regions=AllEC2Regions+ec2regions
                else:
                    nowTotalInUse=nowTotalInUse-detachAmount
        
    
                    reponse=call_detachEC2(userId,AllEC2Regions[:detachAmount],AllEC2Ids[:detachAmount])
                    AllEC2Regions=AllEC2Regions[detachAmount:]
                    AllEC2Ids=AllEC2Ids[detachAmount:]
        whilecount=whilecount+1 
        
    logger.info("===Ave Attach Time----")
    logger.info(AttachWaitingTime)
    logger.info(total/len(AttachWaitingTime))

   
def process(event, context):
    body=event['body']
    body= json.loads(body)
    
    integrationTest_singleRegion_random('ap-east-1',body)
    
  ################################################
    # userId="integrationtest"
    # appIds=[
    #     "bbee173e-955c-4f3d-a0b9-b37f45502dc2",
    #     "f16e6a8c-4091-4453-a1c7-1cbc6814d9c4"
    #     ]

    # logger.info("======== integrationTest_singleRegion_random------")
    # response=call_attachEC2(userId,'ap-east-1',3,appIds)
    
    # logger.info("========== call_attachEC2 -------------")
    # logger.info(response)
    # ec2ids,ec2regions=processPoolItemsToAPIFormat(response)
    # logger.info(ec2ids)
    # logger.info(ec2regions)
    
    
    #######################################
    # userId="integrationtest"
    # regions=["ap-east-1"]
    # ec2ids=["i-0032e1a77562710f2"]
    # call_detachEC2(userId,regions,ec2ids)
    
    
    
    
    
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
    