import json
import boto3
import logging
import boto3
import sys
from datetime import datetime, timedelta,date
from dateutil.relativedelta import relativedelta

from boto3.dynamodb.conditions import Key, Attr

import time
from uuid import uuid4

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)
AccessControlAllowOrigin="https://d1wzk0972nk23y.cloudfront.net"

def progress_bar(seconds):
    """Shows a simple progress bar in the command window."""
    for _ in range(seconds):
        time.sleep(1)
        print('.', end='')
        sys.stdout.flush()
    print()

def setup(iam_resource):

    try:
        userName=f'enterpriseUser-{uuid4()}'
        logger.info(userName)
        user = iam_resource.create_user(UserName=userName)
        logger.info("==============user==============")
        logger.info(user)
        print(f"Created user {user.name}.")
    except ClientError as error:
        
        logger.info("==============can't create user==============")
        print(f"Couldn't create a user for the demo. Here's why: "
              f"{error.response['Error']['Message']}")
        raise

    try:
        user_key = user.create_access_key_pair()
        print(f"Created access key pair for user.")
        logger.info("==============user_key==============")
        logger.info(user_key)
    except ClientError as error:
        print(f"Couldn't create access keys for user {user.name}. Here's why: "
              f"{error.response['Error']['Message']}")
        raise
    
    print(f"Wait for user to be ready.", end='')
    progress_bar(10)

    try:
        role = iam_resource.create_role(
            RoleName=f'demo-role-{uuid4()}',
            AssumeRolePolicyDocument=json.dumps({
                'Version': '2012-10-17',
                'Statement': [{
                    'Effect': 'Allow',
                    'Principal': {'AWS': user.arn},
                    'Action': 'sts:AssumeRole'}]}))
        print(f"Created role {role.name}.")
    except ClientError as error:
        print(f"Couldn't create a role for the demo. Here's why: "
              f"{error.response['Error']['Message']}")
        raise

    try:
        rolepolicy=f'demo-policy-{uuid4()}'
        policy = iam_resource.create_policy(
            PolicyName=f'demo-policy-{uuid4()}',
            PolicyDocument=json.dumps({
                'Version': '2012-10-17',
                'Statement': [
                    {
                    'Effect': 'Allow',
                    'Action': '*',
                    'Resource': '*'},
                     {
                        "Sid": "VisualEditor0",
                        "Effect": "Allow",
                        "Action": "ssm:SendCommand",
                        "Resource": "*"
                    }
                    
                    ]}
                    ))
                    
                 
        role.attach_policy(PolicyArn=policy.arn)
        print(f"Created policy {policy.policy_name} and attached it to the role.")
    except ClientError as error:
        print(f"Couldn't create a policy and attach it to role {role.name}. Here's why: "
              f"{error.response['Error']['Message']}")
        raise

    try:
        userpolicy=f'demo-user-policy-{uuid4()}'
        user.create_policy(
            PolicyName=userpolicy,
            PolicyDocument=json.dumps({
                'Version': '2012-10-17',
                'Statement': [{
                    'Effect': 'Allow',
                    'Action': 'sts:AssumeRole',
                    'Resource': role.arn}]}))
        print(f"Created an inline policy for {user.name} that lets the user assume "
              f"the role.")
    except ClientError as error:
        print(f"Couldn't create an inline policy for user {user.name}. Here's why: "
              f"{error.response['Error']['Message']}")
        raise

    print("Give AWS time to propagate these new resources and connections.", end='')
    progress_bar(10)

    return user, user_key, role,userpolicy,rolepolicy


def deleteIAMUser(user,role):
   
    try:
        for attached in role.attached_policies.all():
            policy_name = attached.policy_name
            role.detach_policy(PolicyArn=attached.arn)
            attached.delete()
            print(f"Detached and deleted {policy_name}.")
        role.delete()
        print(f"Deleted {role.name}.")
    except ClientError as error:
        print("Couldn't detach policy, delete policy, or delete role. Here's why: "
              f"{error.response['Error']['Message']}")
        raise

    try:
        for user_pol in user.policies.all():
            user_pol.delete()
            print("Deleted inline user policy.")
        for key in user.access_keys.all():
            key.delete()
            print("Deleted user's access key.")
        user.delete()
        print(f"Deleted {user.name}.")
    except ClientError as error:
        print("Couldn't delete user policy or delete user. Here's why: "
              f"{error.response['Error']['Message']}")



def createIAMUser():
    
    iam_resource = boto3.resource('iam')
    user = None
    role = None
    logging.info(iam_resource)
    try:
        logging.info("=-")
        user, user_key, role,userpolicy,rolepolicy = setup(iam_resource)
       
       
    except Exception as e:
        logger.info(e)
    
    finally:
        if user is not None and role is not None:
            # teardown(user, role)
            return user, user_key, role,userpolicy,rolepolicy
        

def lambda_handler(event, context):
    logger.info("==========event=========")
    logger.info(event)
    logger.info("==========context=========")
    logger.info(context)
    try:

    
        if event!=None:
            if event['action']=='createIAMUser':
                dynamodb = boto3.client('dynamodb')
                dynamodb_resource = boto3.resource('dynamodb', region_name='us-east-1')

                
                table = dynamodb_resource.Table('VBS_Enterprise_Info')
                
            
                response = table.query(
                KeyConditionExpression=Key('userid').eq('Enterprise_User_Service')
                )

                logger.info("===========db response")
                logger.info(response)
                if 'Items' in response.keys():
                    item = response['Items'][0]

                    if item!=None:
                        if item['awsUserName']!=None:
                            client = boto3.client('iam')
                            iam_resource = boto3.resource('iam')
                            response_iam = client.list_users()
                            for item2 in response_iam['Users']:
                                if item2['UserName']==item['awsUserName']:
                                    
                                    username=item['awsUserName']
                                    rolename=item['iam_role']
                                    userpolicy=item['userpolicy']
                                    rolepolicy=item['rolepolicy']
                                

                                    
                                    user=iam_resource.User(username)
                                    role=iam_resource.Role(rolename)
                                    deleteIAMUser(user,role)
                                
                                
                                
                            
                            response_2=dynamodb.delete_item(TableName='VBS_Enterprise_Info',Key={'userid':{'S':'Enterprise_User_Service'}})
                            

                
                
                user, user_key, role,userpolicy,rolepolicy =createIAMUser()
                logger.info(user)
                logger.info(user_key)
                logger.info(role)
                
                if user!=None:
                    # user=response[0] 
                    # user_key=response[1]
                    # role =response[2]
                    

                    response3=dynamodb.put_item(TableName='VBS_Enterprise_Info', Item={
                        'userid':{'S':'Enterprise_User_Service'},
                        'awsUserName':{'S':str(user_key.user_name)},
                        'keypair_id':{'S':str(user_key.id)},
                        'keypair_secret':{'S':str(user_key.secret)},
                        'iam_role':{'S':str(role.name)},
                        'iam_role_arn':{'S':str(role.arn)},
                        'userpolicy':{'S':str(userpolicy)},
                        'rolepolicy':{'S':str(rolepolicy)},
                        })
                
                                
                alldata=[user, user_key, role,userpolicy,rolepolicy,response3]
                return {
                'headers':{
                    "Access-Control-Allow-Headers" : "Content-Type",
                    "Access-Control-Allow-Origin": AccessControlAllowOrigin,
                    "Access-Control-Allow-Methods": "*"
                },
                'statusCode': 200,
                'body': json.dumps(alldata)
                }
            elif (event['action']=='createTempCredentials'):

                dynamodb_resource = boto3.resource('dynamodb', region_name='us-east-1')

                
                table = dynamodb_resource.Table('VBS_Enterprise_Info')
                
            
                response = table.query(
                KeyConditionExpression=Key('userid').eq('Enterprise_User_Service')
                )
                if 'Items' in response.keys():
                    item = response['Items'][0]
                    sts_client = boto3.client(
                        'sts', aws_access_key_id=item['keypair_id'], aws_secret_access_key=item['keypair_secret'])
                    try:
                        session_name=f'enterpriseUser_session-{uuid4()}'
                        response = sts_client.assume_role(
                            RoleArn=item['iam_role'], RoleSessionName=session_name)
                        temp_credentials = response['Credentials']
                        logging.info(f"Assumed role {temp_credentials} and got temporary credentials.")
                        return {
                            'headers':{
                                "Access-Control-Allow-Headers" : "Content-Type",
                                "Access-Control-Allow-Origin": AccessControlAllowOrigin,
                                "Access-Control-Allow-Methods": "*"
                            },
                            'statusCode': 200,
                            'body': json.dumps(temp_credentials)
                            }
                      
                    except ClientError as error:
                        logging.info(f"Couldn't assume rol. Here's why: "
                            f"{error.response['Error']['Message']}")
                      
                        
                        raise
                    
            elif (event['action']=='test'):
                dynamodb_resource = boto3.resource('dynamodb', region_name='us-east-1')

                
                table = dynamodb_resource.Table('VBS_Enterprise_Info')
                
                
                response = table.query(
                KeyConditionExpression=Key('userid').eq('Enterprise_User_Service')
                )
                item = response['Items'][0]
                
                sts_client = boto3.client(
                                    'sts', aws_access_key_id=item['keypair_id'], aws_secret_access_key=item['keypair_secret'])
                try:
                    response = sts_client.assume_role(
                        RoleArn=item['iam_role_arn'], RoleSessionName="jiojo")
                    temp_credentials = response['Credentials']
                    print(f"Assumed role {item['iam_role_arn']} and got temporary credentials.")
                except ClientError as error:
                    print(f"Couldn't assume role {item['iam_role_arn']}. Here's why: "
                          f"{error.response['Error']['Message']}")
                    raise
            
                # Create an S3 resource that can access the account with the temporary credentials.
               
                # temp_credentials = stsresponse ['Credentials']
                # newsession_id = stsresponse["Credentials"]["AccessKeyId"]
                # newsession_key = stsresponse["Credentials"]["SecretAccessKey"]
                # newsession_token = stsresponse["Credentials"]["SessionToken"]
                
                
                session=boto3.session.Session( 
                      region_name=event['region'],
                  aws_access_key_id=temp_credentials["AccessKeyId"],
                  aws_secret_access_key=temp_credentials["SecretAccessKey"],
                  aws_session_token=temp_credentials['SessionToken'])
                  
                ssm_client=session.client('ssm')
                
                logging.info(session)
                logging.info(ssm_client)
                instanceId=event['ec2id']
                testCommand = ssm_client.send_command( 
                InstanceIds=[instanceId], 
                    DocumentName='AWS-RunPowerShellScript', 
                    Comment=instanceId+'_command', 
                    
                    Parameters={ 
                        "commands":[ 
                            "Get-Process"
                            ]  
                        
                    } )
                logging.info(testCommand)
                    
                    
                    
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


        
        
        alldata=[{
            "status":'fail',
            "data":"Please check the parameters."
        }]
        return {
                'headers':{
                    "Access-Control-Allow-Headers" : "Content-Type",
                    "Access-Control-Allow-Origin": AccessControlAllowOrigin,
                    "Access-Control-Allow-Methods": "*"
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
                    "Access-Control-Allow-Origin": AccessControlAllowOrigin,
                    "Access-Control-Allow-Methods": "*"
                },
                
            }
   
