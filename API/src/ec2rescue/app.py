import json
import boto3
import logging
import boto3
import sys
from datetime import datetime, timedelta,date
from dateutil.relativedelta import relativedelta
import time
from uuid import uuid4
from boto3.dynamodb.conditions import Key, Attr
logger = logging.getLogger()
logger.setLevel(logging.INFO)
AccessControlAllowOrigin="https://d1wzk0972nk23y.cloudfront.net"
def get_credential():
    dynamodb_resource = boto3.resource('dynamodb', region_name='us-east-1')

                
    table = dynamodb_resource.Table('VBS_Enterprise_Info')
    
    
    response = table.query(
    KeyConditionExpression=Key('userid').eq('Enterprise_User_Service')
    )
    item = response['Items'][0]
    
    sts_client = boto3.client(
                        'sts', aws_access_key_id=item['keypair_id'], aws_secret_access_key=item['keypair_secret'])
    try:
        session_name=f'enterpriseUser_session-{uuid4()}'
        response = sts_client.assume_role(
            RoleArn=item['iam_role_arn'], RoleSessionName=session_name)
        temp_credentials = response['Credentials']
        print(f"Assumed role {item['iam_role_arn']} and got temporary credentials.")
    except ClientError as error:
        print(f"Couldn't assume role {item['iam_role_arn']}. Here's why: "
              f"{error.response['Error']['Message']}")
        raise
    return temp_credentials
    
def get_result(ssm_client,testCommand,instanceId):
    time.sleep(2)
    Flag=True
    while(Flag):
        response_command = ssm_client.get_command_invocation(
          CommandId=testCommand['Command']['CommandId'],
          InstanceId=instanceId,
         
        )
    
        if response_command['Status'] not in ['Pending','InProgress','Delayed']:
            logger.info(response_command) 
            Flag=False
            data=response_command
    logger.info("============Response=============")
    logger.info(data)    
    return data
    
def lambda_handler(event, context):
    logger.info(event.keys())
    
    try:
        if ('body' in event.keys()) & ('pathParameters' in event.keys()):
            
            body=event['body']
            body= json.loads(body)
            logger.info(event['pathParameters'])
            # if ('ec2ids' in body.keys())&('regions' in body.keys()):
            if True:
            # if "ec2id" in event['pathParameters'].keys() &"userid" in event['pathParameters'].keys() & "region" in body.keys() & "action" in body.keys():
                
               
                userid=event['pathParameters']['userid']
                
                instanceId=event['pathParameters']['ec2id']
                region=body['region']
                action=body['action']
                
                temp_credentials=get_credential()      
                        
                       
                client = boto3.client('ssm')
                ssm = boto3.client('ssm' )
            

                session=boto3.session.Session( 
                      region_name=region,
                  aws_access_key_id=temp_credentials["AccessKeyId"],
                  aws_secret_access_key=temp_credentials["SecretAccessKey"],
                  aws_session_token=temp_credentials['SessionToken'])
                  
                ssm_client=session.client('ssm')
                
                logging.info(session)
                logging.info(ssm_client)
              
       
                if body['action']=='EC2RescueInitialize':
                    command=[
                    "Invoke-WebRequest -Uri \"https://s3.amazonaws.com/ec2rescue/windows/EC2Rescue_latest.zip?x-download-source=docs\" -OutFile \"./EC2Rescue_latest.zip\"",
                    "Expand-Archive -Path \"./EC2Rescue_latest.zip\"",
                    "Get-ChildItem \"./EC2Rescue_latest\""
                        ]
                elif body['action']=='EC2Rescue-collect-all':
                    command=[
                    "Remove-Item -Path ./EC2Rescue_latest/output.txt -Force",
                    "Start-Process -FilePath \"./EC2Rescue_latest/EC2RescueCmd.exe\" -ArgumentList \"/accepteula /online /collect:all /output:./EC2Rescue_latest/output.txt\"",
                        ]
                elif body['action']=='EC2Rescue-collect-eventlog':
                    command=[
                    "Remove-Item -Path ./EC2Rescue_latest/output.txt -Force",
                    "Start-Process -FilePath \"./EC2Rescue_latest/EC2RescueCmd.exe\" -ArgumentList \"/accepteula /online /collect:eventlog /output:./EC2Rescue_latest/output.txt\"",
                        ]
                elif body['action']=='EC2Rescue-collect-sysprep':
                    command=[
                    "Remove-Item -Path ./EC2Rescue_latest/output.txt -Force",
                    "Start-Process -FilePath \"./EC2Rescue_latest/EC2RescueCmd.exe\" -ArgumentList \"/accepteula /online /collect:sysprep /output:./EC2Rescue_latest/output.txt\"",
                        ]
                elif body['action']=='EC2Rescue-collect-egpu':
                    command=[
                    "Remove-Item -Path ./EC2Rescue_latest/output.txt -Force",
                    "Start-Process -FilePath \"./EC2Rescue_latest/EC2RescueCmd.exe\" -ArgumentList \"/accepteula /online /collect:egpu /output:./EC2Rescue_latest/output.txt\"",
                        ]         
                elif body['action']=='EC2Rescue-collect-driver-setup':
                    command=[
                    "Remove-Item -Path ./EC2Rescue_latest/output.txt -Force",
                    "Start-Process -FilePath \"./EC2Rescue_latest/EC2RescueCmd.exe\" -ArgumentList \"/accepteula /online /collect:egpu /output:./EC2Rescue_latest/output.txt\"",
                        ]
                elif body['action']=='EC2Rescue-rescue-network':
                    command=[
                    "Remove-Item -Path ./EC2Rescue_latest/output.txt -Force",
                    "Start-Process -FilePath \"./EC2Rescue_latest/EC2RescueCmd.exe\" -ArgumentList \"/accepteula /offline:xvdf /rescue:network /output:./EC2Rescue_latest/output.txt\"",
                        ]
                       
                elif body['action']=='EC2Rescue-get-result':
                    command=[
                    "Get-Content ./EC2Rescue_latest/output.txt"
                        ]
                    
                logger.info(command)    
                logger.info(instanceId)    
       
                testCommand = ssm_client.send_command( 
                InstanceIds=[instanceId], 
                    DocumentName='AWS-RunPowerShellScript', 
                    Comment=instanceId+'_command', 
                    Parameters={ 
                        "commands":command
                    } )
                
                logging.info(testCommand)
                logger.info( testCommand )
                data=get_result(ssm_client,testCommand,instanceId)
                
                     
                json_data = [{
                                "status":"success",
                                "data": data
                                
                              }]
                                
                
                return {
                'headers':{
                    "Access-Control-Allow-Headers" : "Content-Type",
                    "Access-Control-Allow-Origin": "http://vbs-user-website-bucket.s3-website-us-east-1.amazonaws.com",
                    "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
                },
                'statusCode': 200,
                'body': json.dumps(json_data)
                }
        
        
        alldata=[{
            "status":'fail',
            "data":"Please check the parameters."
        }]
        return {
                'headers':{
                    "Access-Control-Allow-Headers" : "Content-Type",
                    "Access-Control-Allow-Origin": "https://d1wzk0972nk23y.cloudfront.net",
                    "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
                },
                'statusCode': 401,
                'body': json.dumps(alldata)
                }
    except Exception as e:
        
        logger.info(e)
        json_data = [{
                        "status":"fail",
                            "data":str(e)
                        }]
        return {
            "statusCode": 402,
            "body": json.dumps({"statusCode": 402,"data": json.dumps(json_data)}),
            "isBase64Encoded": False,
            'headers':{
                    "Access-Control-Allow-Headers" : "Content-Type",
                    "Access-Control-Allow-Origin": "https://d1wzk0972nk23y.cloudfront.net",
                    "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
                },
                
            }
   
