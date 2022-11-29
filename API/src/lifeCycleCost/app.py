import json
import boto3
import logging
import boto3
import sys
from datetime import datetime, timedelta,date
from dateutil.relativedelta import relativedelta
from boto3.dynamodb.conditions import Key, Attr
logger = logging.getLogger()
logger.setLevel(logging.INFO)
AccessControlAllowOrigin="https://d1wzk0972nk23y.cloudfront.net"
CPUUtilization_threshold=11
def process(event, context):
    try: 
        dynamodb_resource = boto3.resource('dynamodb', region_name='us-east-1')
        dynamodb = boto3.client('dynamodb')
        table = dynamodb_resource.Table('VBS_Instances_Information')
        
        response = table.scan()
        
        logger.info("============response=============")
        logger.info(response) 
        data=[]
        for item in response['Items']:
            ec2id=item['id']
            region=item['region']
            cloudwatch = boto3.client('cloudwatch',region_name=region)
            currentTime=datetime.now()
            response = cloudwatch.get_metric_statistics(
                        Namespace='AWS/EC2',
                        MetricName='CPUUtilization',
                        Dimensions=[
                            {
                            'Name': 'InstanceId',
                            'Value': ec2id
                            },
                        ],
                        StartTime=currentTime- timedelta(seconds=600),
                        EndTime=currentTime,
                        Period=60,
                        Statistics=[
                            'Average',
                        ],
                       
                    )
            data.append(str(response))
            logger.info("============response=============")
            logger.info(ec2id)
            logger.info(response)
            ec2 = boto3.client('ec2',region_name=region)
            instance_status=None
            try:
                instance_status = ec2.describe_instance_status(
                        InstanceIds=[
                            ec2id
                        ],
                    )
            except:
                response_2=dynamodb.delete_item(TableName='VBS_Instances_Information',Key={'id':{'S':ec2id}})
                
               
            logger.info(instance_status)
            if instance_status!=None:
                # stringlog=f'{str(response['Datapoints'][0]['Average'])} vs {str(CPUUtilization_threshold)}'
                logger.info(response['Datapoints'][0]['Average'])
                
                if response['Datapoints'][0]['Average']<CPUUtilization_threshold:
                    logger.info(instance_status['InstanceStatuses'][0]['InstanceState'])
                    if instance_status['InstanceStatuses'][0]['InstanceState']['Name']=='running':
                        response_1 = ec2.stop_instances(
                            InstanceIds=[ec2id]
                            )
                        
                        
                        
                 
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
            
            
