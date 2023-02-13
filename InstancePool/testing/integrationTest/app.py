import re
import boto3
import json
import boto3
import logging
import boto3
import datetime
import uuid
import requests
AccessControlAllowOrigin="https://d1wzk0972nk23y.cloudfront.net"
logger = logging.getLogger()
logger.setLevel(logging.INFO)
class CustomError(Exception):
  pass
def call_attachEC2(contentid,region):
  baseUrl="https://vxtiwk095b.execute-api.us-east-1.amazonaws.com/prod/contents/"
 
  headers = {
        'Authorization':'Basic cnJ0ZWFtOmlsb3ZlaHRj',
        'accept': 'application/json' 
    }

  bodyData={""}
  req = requests.post(
   baseUrl+contentid+"/"+region,
   headers=headers,
   data=bodyData
    )
  resp_dict = req.json()
  logger.info("======== req ------")
  logger.info(resp_dict['snapshot_id'])
  return resp_dict['snapshot_id']

def integrationTest_singleRegion_random(regionId,tries):
    
   
def process(event, context):
    try:
            logger.info(event)
            body=event['body']
            body= json.loads(body)
            pathParameters=event['pathParameters']
            
    except:
        raise CustomError("Please check the parameters.")

    #########code here
    ############# Enlarge Running Pool #####################
    


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
    