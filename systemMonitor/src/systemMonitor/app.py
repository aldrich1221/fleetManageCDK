import json
import boto3
import logging
import boto3
import sys
from datetime import datetime, timedelta,date
from dateutil.relativedelta import relativedelta
from boto3.dynamodb.conditions import Key, Attr
import datetime

import requests

logger = logging.getLogger()
logger.setLevel(logging.INFO)
AccessControlAllowOrigin="https://d1wzk0972nk23y.cloudfront.net"
CPUUtilization_threshold={'g4dn.xlarge':20,'t3.medium':15}


def send_CostUsage_Daily():
    
    
    
    
    
    
    
    
    now_datetime = datetime.datetime.now()
    dateTimeStr_new = now_datetime.strftime("%Y-%m-%d/%H:%M:%S:%f")
    
    today = date.today()
    d = today.strftime("%Y-%m-%d")
    one_days = today + relativedelta(days=-1)
    d2=one_days.strftime("%Y-%m-%d")
    
    seven_days = today + relativedelta(days=-7)
    d3=seven_days.strftime("%Y-%m-%d")
    
    client = boto3.client('ce')

    costMethod='UnblendedCost'
    # costMethod='AmortizedCost'
    result = client.get_cost_and_usage(
    TimePeriod = {
        'Start': d2,
        'End': d
    },
    Granularity = 'DAILY',
    Metrics = [costMethod],

    )
    logger.info("============result=============")
    logger.info(result)
    dailycosts=[]
    costarray=result['ResultsByTime']
    for costdayitem in costarray:
        
        x =float(costdayitem["Total"][costMethod]["Amount"])
        new_x=f'{x:.0f}'

        dailycosts.append(float(costdayitem["Total"][costMethod]["Amount"]))
        yesterdayCost=new_x
    
    logger.info("dailycosts")
    logger.info(dailycosts)
    
    
  
   
    result2 = client.get_cost_and_usage(
    TimePeriod = {
        'Start': d3,
        'End': d
    },
    Granularity = 'DAILY',
    Metrics = [costMethod],

    )
    logger.info("============result2=============")
    logger.info(result2)
    
    costarray=result2['ResultsByTime']
    total=0
    weeklycosts=[]
    for costdayitem in costarray:
        thisWeekCost=costdayitem["Total"][costMethod]["Amount"]
        x =float(costdayitem["Total"][costMethod]["Amount"])
        new_x=f'{x:.3f}'
        
        weeklycosts.append(float(new_x))
        
        total=total+x
        
    
    average=total/len(weeklycosts)
    average_str=f'{average:.0f}'
        
    
    # NewCostString="Yesterday\n"+str(yesterdayCost) +"USD"
    NewCostString= str(yesterdayCost) +"USD"
    
    # StringCost="Yesterday  (USD) : "+str(yesterdayCost) +"\n"
    
    
    # StringCost=StringCost+" Average in seven days (USD) : "+average_str+"\n  Seven days (USD) : "+json.dumps(weeklycosts)
    # StringCost=json.dumps(costarray)
    
    
    # baseUrl="https://htcazurehtc.webhook.office.com/webhookb2/d2e982b3-e509-4760-b794-2b9c84a08369@afb5d3cf-2693-47e7-ade9-696a806ba95a/IncomingWebhook/53c1d12a4a12433497f9999090078e35/ff5f9314-b026-4cb9-8722-be00cd71cbcd"
    baseUrl="https://htcazurehtc.webhook.office.com/webhookb2/d2e982b3-e509-4760-b794-2b9c84a08369@afb5d3cf-2693-47e7-ade9-696a806ba95a/IncomingWebhook/2ee2102aa5e74e069a09c923e5790220/ff5f9314-b026-4cb9-8722-be00cd71cbcd"
    
    # json_data={
    #     'Text':"|Cost| "+ StringCost+' |Time| '+dateTimeStr_new
    # }
    json_data={
        'title':"Yesterday",
        'Text':NewCostString
    }
    req = requests.post(
    baseUrl,
    data=json.dumps(json_data)
      )
    resp_dict = req.json()
   
    logger.info(resp_dict)


def process(event, context):
   

    try: 

        send_CostUsage_Daily()

        data="good"    
        return data            
    except Exception as e:
        raise
   

def lambda_handler(event, context):
    try:
        if True:
        # if ('body' in event.keys()) & ('pathParameters' in event.keys()):
                
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
            
            
