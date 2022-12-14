import re
import boto3
import json
import boto3
import logging
import boto3
import sys
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
            
    except:
        raise CustomError("Please check the parameters.")

    #########code here
    try:
        MetricList=[
                    'CPUUtilization',
                    'NetworkIn',
                    'NetworkOut',
                    'NetworkPacketsIn',
                    'NetworkPacketsOut',
                    'StatusCheckFailed_Instance',
                    'EBSIOBalance%',
                    'CPUCreditUsage',
                    'DiskReadBytes',
                    'DiskWriteBytes']
        alldata=[]
        format='%Y-%m-%d'
        if 'startdate' in body.keys(): 
            datestart_string=body['startdate']
        else:
            datestart_string=datetime.today().strftime('%Y-%m-%d')
            dateend_string=datetime.today().strftime('%Y-%m-%d')
        
        if 'enddate' in body.keys():  
            dateend_string=body['enddate']
        else:
            dateend_string=datetime.today().strftime('%Y-%m-%d')
        alldata=[]
        for iec2 in range(len(body["ec2ids"])):
            
            region=body["regions"][iec2]
            ec2id=body["ec2ids"][iec2]


            cloudwatch = boto3.client('cloudwatch',region_name=region)
            data=[]
            for metric in MetricList:
                response = cloudwatch.get_metric_statistics(
                    Namespace='AWS/EC2',
                    MetricName=metric,
                    Dimensions=[
                        {
                        'Name': 'InstanceId',
                        'Value': ec2id
                        },
                    ],
                    # StartTime=datetime.strptime(datestart_string, format) - timedelta(seconds=300),
                    # EndTime=datetime.strptime(dateend_string, format),
                    StartTime=datetime.now()- timedelta(seconds=300),
                    EndTime=datetime.now(),
                    Period=60,
                    Statistics=[
                        'Average',
                    ],
                
                )
                logger.info("============response=============")
                logger.info(response)  
                
                
                newdata={
                    "label":response['Label'],
                    "datapoints":[{'Timestamp':x['Timestamp'].strftime(format),'Average':x['Average'],'Unit':x['Unit']} for x in response['Datapoints']]
                }
                data.append(newdata)
            
            

            ec2 = boto3.client('ec2',region_name=region)
            instance_response = ec2.describe_instances(InstanceIds=[
                    ec2id
                ],)

            newdata={
                    "label":"InstanceInfo",
                    "datapoints":[instance_status]
                }

            instance_status = ec2.describe_instance_status(
                InstanceIds=[
                    ec2id
                ],
            )
            
            newdata={
                    "label":"InstanceStatuses",
                    "datapoints":[instance_status]
                }
            data.append(newdata)
            alldata.append({
                    "ec2id":ec2id,
                    "data":data
                })
        return alldata

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
    