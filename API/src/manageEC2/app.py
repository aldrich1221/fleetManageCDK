import re
import boto3
import json
import time
import logging

import os
from boto3.dynamodb.conditions import Key, Attr
import logging
from datetime import datetime
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
            
            DEFAULTREGION = os.environ['AWS_REGION'] 
            USERID=pathParameters['userid']
            ACTION=pathParameters['actionid']
            INSTANCEIDS = body['ec2ids']
            REGIONS =body['ec2regions']
            if len(INSTANCEIDS)!=len(REGIONS):
              raise CustomError("the number of ec2ids  must be equal to ec2regions")
    except:
        raise CustomError("Please check the parameters.")

    #########code here
    
    
    


    try:
      dynamodb_resource = boto3.resource('dynamodb', region_name=DEFAULTREGION)
      dynamodb = boto3.client('dynamodb')
      allresponsedata=[]
      for iec2 in range(len(INSTANCEIDS)):
        REGION=REGIONS[iec2]
        instance_id=INSTANCEIDS[iec2]
        ec2 = boto3.client('ec2', region_name=REGION)
        ec2_resource = boto3.resource('ec2')
        if ACTION=="stop":
          response_1 = ec2.stop_instances(
              InstanceIds=[
                  instance_id,
              ]
              )

          # input_str = '21/01/24 11:04:19'

          # dt_object = datetime.strptime(
          # input_str, '%d/%m/%y %H:%M:%S')

          # print("The type of the input date string now is: ",
          # type(dt_object))
          x = datetime.now()
          format_string='%d/%m/%y %H:%M:%S'
          datetimeString = x.strftime(format_string)


          table = dynamodb_resource.Table('VBS_Instances_Information')
          response = table.update_item(
                            Key={
                                'id':instance_id,
                            },
                            UpdateExpression="set publicIP = :r,publicDnsName= :p,launchtime= :q,stoppedtime= :s",
                            ExpressionAttributeValues={
                                ':r': "",
                                ':p': "",
                                ':q': "",
                                ':s': datetimeString,
                                
                            },
                            ReturnValues="UPDATED_NEW"
                        )
          json_data = {"data":  [response_1,response] , 
                            
                            "status":"success",
                        
                          }
          allresponsedata.append(json_data)
        elif ACTION=='check':
            
            instance_status = ec2.describe_instance_status(
                    InstanceIds=[
                        instance_id
                    ],
                )
               
            json_data = {"data":  instance_status, 
                          "Action":"check",
                          "status":"success",
                        }
            allresponsedata.append(json_data)
        elif ACTION=='start':
            logger.info("============action start=============")
            t1 = datetime.now()
            print('Start time:', t1.time())
            response_1 = ec2.start_instances(
            InstanceIds=[
                instance_id,
            ]
            )
            
            state='pending'
            publicIP=''
            publicDnsName=''
            launchtime=''
            while(state=='pending'):
              Myec2= ec2.describe_instances()
            
              for pythonins in Myec2['Reservations']:
                for printout in pythonins['Instances']:
                  if printout['InstanceId']==instance_id:
                    logger.info("============instance_data=============")
                    logger.info(printout)
                    if 'PublicIpAddress' in printout.keys():
                      state='done'
                    
                      publicIP=printout['PublicIpAddress']
                      publicDnsName=printout['PublicDnsName']
                      launchtime=printout['LaunchTime'].strftime("%Y-%m-%d,%H:%M:%S")

            
            # logger.info("============Time compare=============")
            t2 = datetime.now()
            logger.info(t1.time())
            logger.info(t2.time())
            # get difference
            delta = t2 - t1
            
            # time difference in seconds
            print(f"Time difference is {delta.total_seconds()} seconds")
            logger.info(f"Time difference is {delta.total_seconds()} seconds")
            
            # time difference in milliseconds
            ms = delta.total_seconds() * 1000
            print(f"Time difference is {ms} milliseconds")
            logger.info(f"Time difference is {ms} milliseconds")
            table = dynamodb_resource.Table('VBS_Instances_Information')
            response = table.update_item(
                            Key={
                                'id':instance_id,
                               
                            },
                            UpdateExpression="set publicIP = :r,publicDnsName= :p,launchtime= :q,stoppedtime= :s",
                            ExpressionAttributeValues={
                                ':r': publicIP,
                                ':p': publicDnsName,
                                ':q': launchtime,
                                ':s': ""
                                
                            },
                            ReturnValues="UPDATED_NEW"
                        )
            
            
            
            json_data = {"data":  [response_1,response] , 
                          "Action":"Started",
                          "status":"success",
                       
                        }
            allresponsedata.append(json_data)
        elif ACTION=='delete':
          
            response_1 = ec2.terminate_instances(
              InstanceIds=[
                  instance_id,
              ]
            )
            
            response_2=dynamodb.delete_item(TableName='VBS_Instances_Information',Key={'id':{'S':instance_id}})
            json_data = {"data": [response_1,response_2], 
                            "Action":"Deleted",
                            "status":"success",
                         
                          }
            allresponsedata.append(json_data)
      return allresponsedata


                        
   

   
        
        
        
            
      
      
     
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
    