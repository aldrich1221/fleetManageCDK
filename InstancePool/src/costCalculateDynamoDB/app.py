import re
import boto3
import json
import boto3
import logging
import boto3
from boto3.dynamodb.conditions import Key, Attr
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
            
    except:
        raise CustomError("Please check the parameters.")

    #########code here
    aciton=pathParameters['acitonId']
    userid=pathParameters['userId']
    
    if aciton=='queryCostInPeriod':
        StartTime=body['StartTime']
        EndTime=body['EndTime']

        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

        table = dynamodb.Table('VBS_User_UsageAndCost')

        response = table.query(
                IndexName="userId_datetime_index",
                KeyConditionExpression=Key('userId').eq(userid) & Key('datetime').between(StartTime,EndTime)
            )
        
        totol_time=0
        MonthDict_time={}
        DayDict_time={}

        totol_cost=0
        MonthDict_cost={}
        DayDict_cost={}

        for item in response['Items']:
            UsageTime_totalseconds=item['UsageTime_totalseconds']['S']
            UsageCost=item['UsageCost']['S']
            
            datetimeStr=item['datetime']['S']
            datestr=datetimeStr.split("/")[0]
            monthstr=datestr.split('-')[0]+"-"+datestr.split('-')[1]
            
            totol_time=totol_time+UsageTime_totalseconds
            totol_cost=totol_cost+UsageCost

            if datestr in DayDict_time.keys():
                DayDict_time[datestr]=DayDict_time[datestr]+UsageTime_totalseconds
            else:
                DayDict_time[datestr]=UsageTime_totalseconds

            if datestr in DayDict_cost.keys():
                DayDict_cost[datestr]=DayDict_cost[datestr]+UsageCost
            else:
                DayDict_cost[datestr]=UsageCost

            
            if monthstr in MonthDict_time.keys():
                MonthDict_time[monthstr]=MonthDict_time[monthstr]+UsageTime_totalseconds
            else:
                MonthDict_time[monthstr]=UsageTime_totalseconds

            if monthstr in MonthDict_cost.keys():
                MonthDict_cost[monthstr]=MonthDict_cost[monthstr]+UsageCost
            else:
                MonthDict_cost[monthstr]=UsageCost

        responseResult={
            'total_usage_time':totol_time,
            'total_usage_cost':totol_cost,
            'monthly_usage_cost':MonthDict_cost,
            'monthly_usage_time':MonthDict_time,
            'daily_usage_cost':DayDict_cost,
            'daily_usage_time':DayDict_time
        }

                

        return responseResult
    
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
    