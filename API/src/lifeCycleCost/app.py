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
def send_cpuUtilization_notification_email(useremail,userid,instanceid):
    ses_client = boto3.client("ses", region_name="us-east-1")
    CHARSET = "UTF-8"
    HTML_EMAIL_CONTENT = """
        <html>
            <head></head>
            <h1 style='text-align:center'>Low CPU Utilization Notification</h1>
            <p>Dear {userid}</p>
            <p>To reduce the cost,we stop the instance {instanceid} with low CPU Utilization</p>

            
            </body>
        </html>
    """

    response = ses_client.send_email(
        Destination={
            "ToAddresses": [
                useremail,
            ],
        },
        Message={
            "Body": {
                "Html": {
                    "Charset": CHARSET,
                    "Data": HTML_EMAIL_CONTENT,
                }
            },
            "Subject": {
                "Charset": CHARSET,
                "Data": "VBS Cloud Notification",
            },
        },
        Source="aldrich_chen@htc.com")

def send_cost_notification_email(useremail,userid,totalcost,detaillink):
    ses_client = boto3.client("ses", region_name="us-east-1")
    CHARSET = "UTF-8"
    HTML_EMAIL_CONTENT = """
        <html>
            <head></head>
            <h1 style='text-align:center'>Cost Notification</h1>
            <p>Dear {userid}</p>
            <p>The total cost in this month is:{totalcost} </p>
            <p>Please see the detail from the link: {detaillink}</p>
            
            
            </body>
        </html>
    """

    response = ses_client.send_email(
        Destination={
            "ToAddresses": [
                useremail,
            ],
        },
        Message={
            "Body": {
                "Html": {
                    "Charset": CHARSET,
                    "Data": HTML_EMAIL_CONTENT,
                }
            },
            "Subject": {
                "Charset": CHARSET,
                "Data": "VBS Cloud Notification",
            },
        },
        Source="aldrich_chen@htc.com")

def process(event, context):
    try: 
        action=event['action']
        if action=='checkAll':
            dynamodb_resource = boto3.resource('dynamodb', region_name='us-east-1')
            dynamodb = boto3.client('dynamodb')
            table = dynamodb_resource.Table('VBS_Instances_Information')
            
            response = table.scan()
            
            logger.info("============response=============")
            logger.info(response) 
            data=[]
            for item in response['Items']:
                ec2id=item['id']
                userid=item['userid']
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
                            table2 = dynamodb_resource.Table('VBS_Enterprise_Info')
                            usertable_response = table2.query(
                            KeyConditionExpression=Key('userid').eq(userid)
                            )
                            item = response['Items'][0]
                            useremail=item['email']
                            send_cpuUtilization_notification_email(useremail,userid,ec2id)


            ##############for cost notif



        elif action=='costNotifyMonthly':
            logger.info("costNotify")
            dynamodb_resource = boto3.resource('dynamodb', region_name='us-east-1')
            dynamodb = boto3.client('dynamodb')
            table = dynamodb_resource.Table('VBS_Enterprise_Info')
            usertable_response = table.scan()
            for item in usertable_response['Items']:
                email=item['email']
                userid=item['userid']
                username=item['username']
                today = date.today()
                d = today.strftime("%Y-%m-%d")
                one_months = today + relativedelta(months=-1)
                d2=one_months.strftime("%Y-%m-%d")
                
                client = boto3.client('ce')
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
                costarray=result['ResultsByTime']
                dailycosts=[]
                for costdayitem in costarray:
                    dailycosts.append(float(costdayitem["Total"]["AmortizedCost"]["Amount"]))
                send_cost_notification_email(useremail,userid,sum(dailycosts),"www.123")
                json_data = [{"data": result, 
                                "status":"Success",
                            }]
        




                        
                 
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
            
            
