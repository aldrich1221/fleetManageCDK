import re
import boto3
import json
import boto3
import logging
import boto3
from datetime import datetime, timedelta,date
from dateutil.relativedelta import relativedelta
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
            userid=pathParameters['userid']
    except:
        raise CustomError("Please check the parameters.")

    #########code here
    try:
        today = date.today()
        d = today.strftime("%Y-%m-%d")
        one_months = today + relativedelta(days=-7)
        d2=one_months.strftime("%Y-%m-%d")
        
        client = boto3.client('ce')
       
        
            
        logger.info("============result=============")
        logger.info(d)
        logger.info(d2)
        result = client.get_cost_and_usage(
        TimePeriod = {
            'Start': d2,
            'End': d
        },
        Granularity = 'DAILY',
        Metrics = ["AmortizedCost"],
        Filter={
            'Tags': {
                'Key': 'owner',
                'Values': [
                    userid,
                ],
                'MatchOptions': ['EQUALS']
            }
        }
        )
        logger.info("============result=============")
        logger.info(result)
        
        json_data = [{"data": result, 
                        "status":"Success",
                    
                    }]
        return json_data
        
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
    