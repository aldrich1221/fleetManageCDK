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
AccessControlAllowOrigin="https://d1wzk0972nk23y.cloudfront.net"
logger = logging.getLogger()
logger.setLevel(logging.INFO)
class CustomError(Exception):
  pass
def call_attachEC2(userId,region,amount,appIds):
  baseUrl="https://f0sobntajc.execute-api.us-east-1.amazonaws.com/prod/v1"
 
  headers = {
        'Authorization':'Basic cnJ0ZWFtOmlsb3ZlaHRj',
        'accept': 'application/json' 
    }
#  userId=pathParameters['userid']
#         regionId=pathParameters['regionid']
#         appIds=body['appIds']
#         amount=body['amount']
# https://mbl4kje11a.execute-api.us-east-1.amazonaws.com/prod/v1/user/{userid}/region/{regionid}
  bodyData={"amount":amount,"appIds":appIds}
  req = requests.post(
   baseUrl+"/user/"+userId+"/region/"+region,
   headers=headers,
   data=bodyData
    )
  resp_dict = req.json()
  logger.info("======== req ------")
  logger.info(resp_dict)
  return resp_dict


def call_detachEC2(userId,regions,ec2ids):
  baseUrl="https://mbl4kje11a.execute-api.us-east-1.amazonaws.com/prod/v1"
 

  headers = {
        'Authorization':'Basic cnJ0ZWFtOmlsb3ZlaHRj',
        'accept': 'application/json' 
    }

      
  bodyData={"instanceIds":ec2ids,"regionids":regions}
  req = requests.post(
   baseUrl+"/user/"+userId,
   headers=headers,
   data=bodyData
    )
  resp_dict = req.json()
  logger.info("======== req ------")
  logger.info(resp_dict)
  return resp_dict

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

def integrationTest_singleRegion_random(regionId,tries):

    userId="integrationtest"
    appIds=[
        "bbee173e-955c-4f3d-a0b9-b37f45502dc2",
        "f16e6a8c-4091-4453-a1c7-1cbc6814d9c4"
        ]

    logger.info("======== integrationTest_singleRegion_random------")
 
    trycount=tries
    allRequestInstanceNums=[]
    for i in range(tries):
        allRequestInstanceNums.append(random.randint(1, 5))

    allRequestInstanceNums_toAttach=allRequestInstanceNums
    allRequestInstanceNums_toDetach=allRequestInstanceNums*-1

    

    random.shuffle(allRequestInstanceNums_toAttach)
    random.shuffle(allRequestInstanceNums_toDetach)


    ####
    allRequestInstanceNums_toAttach=[5,3]
    allRequestInstanceNums_toDetach=[4]

    nowTotalInUse=0
    attachIndex=0
    detachIndex=0
    AllEC2Ids=[]
    AllEC2Regions=[]

    while (len(allRequestInstanceNums_toAttach)>0) or (len(allRequestInstanceNums_toDetach)>0):
        
        if random.random()>0.5:
            attachAmount=allRequestInstanceNums_toAttach.pop()
            nowTotalInUse=nowTotalInUse+attachAmount
            reponse=call_attachEC2(userId,regionId,attachAmount,appIds)
            ec2ids,ec2regions=processPoolItemsToAPIFormat(reponse)
            AllEC2Ids=AllEC2Ids+ec2ids
            AllEC2Regions=AllEC2Regions+ec2regions
        else:
            detachAmount=allRequestInstanceNums_toDetach.pop()

            if nowTotalInUse<detachAmount:
                allRequestInstanceNums_toDetach.append(detachAmount)

                attachAmount=allRequestInstanceNums_toAttach.pop()
                nowTotalInUse=nowTotalInUse+attachAmount
                reponse=call_attachEC2(userId,regionId,attachAmount,appIds)
                ec2ids,ec2regions=processPoolItemsToAPIFormat(reponse)
                AllEC2Ids=AllEC2Ids+ec2ids
                AllEC2Regions=AllEC2Regions+ec2regions
            else:
                nowTotalInUse=nowTotalInUse-detachAmount


                reponse=call_detachEC2(userId,AllEC2Regions[:detachAmount],AllEC2Ids[:detachAmount])
                AllEC2Regions=AllEC2Regions[detachAmount:]
                AllEC2Ids=AllEC2Ids[detachAmount:]
                
        
        

   
def process(event, context):
    try:
            logger.info(event)
            body=event['body']
            if type(body)!=type(dict()):
              body= json.loads(body)
            # body= json.loads(body)
            # pathParameters=event['pathParameters']
            
    except:
        raise CustomError("Please check the parameters.")

    #########code here
    ############# Enlarge Running Pool #####################
    integrationTest_singleRegion_random('ap-east-1',3)


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
    