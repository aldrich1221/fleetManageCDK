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
CPUUtilization_threshold={'g4dn.xlarge':20,'t3.medium':15}
def send_cpuUtilization_notification_email(useremail,userid,instanceid):
    ses_client = boto3.client("ses", region_name="us-east-1")
    CHARSET = "UTF-8"
    HTML_EMAIL_CONTENT = f"""
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
        Source="admin@tzuchuan.info")


def send_deleteInstance_notification_email_firstTime(useremail,userid,instanceid):
    try:
        ses_client = boto3.client("ses", region_name="us-east-1")
        CHARSET = "UTF-8"
        HTML_EMAIL_CONTENT = f"""
            <html>
                <head></head>
                <h1 style='text-align:center'>Low CPU Utilization Notification</h1>
                <p>Dear {userid}</p>
                <p>After we analyze your activity on our Cloud Platform ,we realize that your registrated server have not been used for a while.
                To reduce the cost,we will delete the instance [ {instanceid} ] tommorow</p>

                
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
            Source="admin@tzuchuan.info")
    except:
        raise

def send_deleteInstance_notification_email_secondTime(useremail,userid,instanceid):
    ses_client = boto3.client("ses", region_name="us-east-1")
    CHARSET = "UTF-8"
    HTML_EMAIL_CONTENT = f"""
        <html>
            <head></head>
            <h1 style='text-align:center'>Low CPU Utilization Notification</h1>
            <p>Dear {userid}</p>
            <p>After we analyze your activity on our Cloud Platform ,we realize that your registrated server have not been used for a while.
            To reduce the cost,we deleted the instance [ {instanceid} ]. You can login into our web to relaunch the instance. Thanks</p>

            
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
        Source="admin@tzuchuan.info")

def send_cost_notification_email(useremail,userid,totalcost,detaillink):
    ses_client = boto3.client("ses", region_name="us-east-1")
    CHARSET = "UTF-8"
    HTML_EMAIL_CONTENT = f"""
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
        Source="admin@tzuchuan.info")

def process(event, context):
   

    try: 

        # action=event['action']
        
        # if action=='checkAll':
        if True:
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
                ec2type=item['instancetype']
                stoppedTime=item['stoppedtime']
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
                    response_describe = ec2.describe_instances(

                                InstanceIds=[
                                    ec2id,
                                ],
                            
                            )
                    
                except:
                    response_2=dynamodb.delete_item(TableName='VBS_Instances_Information',Key={'id':{'S':ec2id}})
                    
                status=response_describe['Reservations'][0]['Instances'][0]['State']['Name']
                logger.info(instance_status)
                logger.info(status)
                if instance_status!=None:
                    # stringlog=f'{str(response['Datapoints'][0]['Average'])} vs {str(CPUUtilization_threshold)}'
                    logger.info("============CPUUtilization_threshold=============")
                    
                    # logger.info(response['Datapoints'][0]['Average'])
                    CPUUtilization_threshold={'g4dn.xlarge':20,'t3.medium':15,'g4dn.2xlarge':20}
                    # if len(instance_status['InstanceStatuses'])>0:
                        # if instance_status['InstanceStatuses'][0]['InstanceState']['Name']=='running':
                    if status=='running':
                            logger.info(instance_status['InstanceStatuses'][0]['InstanceState'])
                            if response['Datapoints'][0]['Average']<CPUUtilization_threshold[ec2type]:
                                response_1 = ec2.stop_instances(
                                    InstanceIds=[ec2id]
                                    )
                                
                                table2 = dynamodb_resource.Table('VBS_Enterprise_Info')
                                usertable_response = table2.query(
                                KeyConditionExpression=Key('userid').eq(userid)
                                )
                                item = usertable_response['Items'][0]
                                useremail=item['email']
                                send_cpuUtilization_notification_email(useremail,userid,ec2id)
                            
                    # elif instance_status['InstanceStatuses'][0]['InstanceState']['Name']=='stopped':
                    elif status=='stopped':
                            # response_1 = ec2.stop_instances(
                            #         InstanceIds=[ec2id]
                            #         )
                                
                            table2 = dynamodb_resource.Table('VBS_Enterprise_Info')
                            usertable_response = table2.query(
                            KeyConditionExpression=Key('userid').eq(userid)
                            )
                            item = usertable_response['Items'][0]
                            useremail=item['email']
                            stoppedTime=item['stoppedtime']
                            
                            x = datetime.now()
                             
                            format_string='%d/%m/%y %H:%M:%S'
                            datetimeString = x.strftime(format_string)
                            

                            logger.info(datetimeString)
                            if stoppedTime=="":
                                response = table.update_item(
                                    Key={
                                        'id':ec2id,
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

                            else:
                                input_str = stoppedTime

                                
                                
                                dt_object = datetime.strptime(input_str, '%d/%m/%y %H:%M:%S')

                                logger.info("============Stopped=============")
                                
                                
                                logger.info(datetimeString)
                                
                                deltaTime=x-dt_object

                                logger.info("=======deltaTime-----")
                                logger.info(deltaTime)


                                ######Eamil 要先認證
                                # deltaTime.days=3.5
                                # response = ses_client.verify_email_address(
                                #     EmailAddress='aldrich_chen@htc.com'
                                # )
    
                                if deltaTime.days>3:
                                    send_deleteInstance_notification_email_firstTime(useremail,userid,ec2id)
                                elif deltaTime.days>4:
                                    send_deleteInstance_notification_email_secondTime(useremail,userid,ec2id)




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
            
            
