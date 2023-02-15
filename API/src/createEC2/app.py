import re
import boto3
import json

import logging

import os
from boto3.dynamodb.conditions import Key, Attr
import logging
from datetime import datetime
import requests
AccessControlAllowOrigin="https://d1wzk0972nk23y.cloudfront.net"
logger = logging.getLogger()
logger.setLevel(logging.INFO)
class CustomError(Exception):
  pass

def getAMI(region):
    baseUrl="https://vxtiwk095b.execute-api.us-east-1.amazonaws.com/prod/images/"
    
    headers = {
          'Authorization':'Basic cnJ0ZWFtOmlsb3ZlaHRj',
          'accept': 'application/json' 
      }

    req = requests.get(
    baseUrl+region,
    headers=headers
      )
    resp_dict = req.json()
    logger.info("======== req ------")
    logger.info(resp_dict)
    return resp_dict
def getSnapshotID(contentid,region):
  baseUrl="https://vxtiwk095b.execute-api.us-east-1.amazonaws.com/prod/contents/"
  #contentid="f16e6a8c-4091-4453-a1c7-1cbc6814d9c4"
  #region="ap-east-1"
  
#   https://vxtiwk095b.execute-api.us-east-1.amazonaws.com/prod/contents/f16e6a8c-4091-4453-a1c7-1cbc6814d9c4/ap-east-1
  headers = {
        'Authorization':'Basic cnJ0ZWFtOmlsb3ZlaHRj',
        'accept': 'application/json' 
    }

  req = requests.get(
   baseUrl+contentid+"/"+region,
   headers=headers
    )
  resp_dict = req.json()
  logger.info("======== req ------")
  logger.info(resp_dict['snapshot_id'])
  return resp_dict['snapshot_id']
def process(event, context):
    try:
            logger.info(event)
            body=event['body']
            logger.info("======== body type------")
            logger.info(type(body)==type(dict()))
            if type(body)!=type(dict()):
              body= json.loads(body)
            logger.info("======== body ------")
            logger.info(body)
            pathParameters=event['pathParameters']
            
            logger.info("======== body ------")
            logger.info(body)
            logger.info("======== pathParameters ------")
            logger.info(pathParameters)
    except Exception as e:
        # raise CustomError("Please check the parameters.")
        raise e

    #########code here
    USERID=pathParameters['userid']
    DEFAULTREGION = os.environ['AWS_REGION'] 
    INSTANCE_TYPE = body['ec2type']
    ZONE=body['ec2zone']
    appids=body['appids']
    userAMI=body['userAMI']
    spotFlag=body['spot']
    amount=body['amount']  
    eventId=body['eventId']
    eventTime=body['eventTime']

    try:
      dynamodb = boto3.client('dynamodb')
      dynamodb_resource = boto3.resource('dynamodb', region_name=DEFAULTREGION)
      
      table = dynamodb_resource.Table('VBS_Region_Info')
      instance_data = table.scan(
                    FilterExpression=Attr("zone").eq(ZONE)
                )
      
      logger.info("============instance_data=============")
      logger.info(instance_data)
      ec2info=instance_data['Items'][0]
      SecurityGroupId=ec2info['securitygroupID']
      # if userAMI=='withsteam':
      #   AMI=ec2info['AMI_withsteam']
      # else:
      #   AMI=ec2info['AMI_withoutsteam']
     
      KEY_NAME=ec2info['keypairName']
      REGION=ec2info['region']
      ARN='arn:aws:iam::867217160264:instance-profile/VBSEC2InstanceProfile'
  
      ec2 = boto3.client('ec2', region_name=REGION)
      AMI=getAMI(REGION) 
      
      # if 'appid' in query.keys():
      if True:
        
        logger.info("============table_content=============")
        BlockDeviceMappings=[{'DeviceName': '/dev/sda1',
                      'Ebs': {
                          'DeleteOnTermination': True,
                          'VolumeSize': 250,
                          
                      },}]
        deviceName=['xvda','xvdb','xvdc','xvdd','xvde','xvdf','xvdg','xvdh','xvdi','xvdj','xvdk','xvdl','xvdm','xvdn','xvdo','xvdp','xvdq','xvdr','xvds','xvdt','xvdu','xvdv','xvdw','xvdx','xvdy','xvdz']
        # table_content = dynamodb_resource.Table('aldrichtest')
        blocki=0
        for appid in appids:
          snapshotid=getSnapshotID(appid,REGION)
          BlockDeviceMappings.append(
                  {
                      'DeviceName': deviceName[blocki],
                      'Ebs': {
                          'DeleteOnTermination': True,
                          'SnapshotId': snapshotid,
                          'VolumeSize': 150,
                          'Encrypted': True
                      },
                   
                  }
                )      
          blocki=blocki+1
          ########################################################################
          # contentData = table_content.scan(
          #             FilterExpression=Attr("appid").eq(str(appid))
                     
          #         )
        
          # logger.info(contentData)
          # for item in contentData['Items']:
          #   if item['region']==REGION:
          #     EBSID=item['volid']      
          #     AppID=item['appid']
          #     BlockDeviceMappings.append(
          #         {
          #             'DeviceName': deviceName[blocki],
          #             'Ebs': {
          #                 'DeleteOnTermination': True,
          #                 'SnapshotId': EBSID,
          #                 'VolumeSize': 150,
          #                 'Encrypted': True
          #             },
                   
          #         }
          #       )      
          #     blocki=blocki+1
          ##################################################################
              
              
        tag_1 = {"Key": "UserID", "Value": "HTC_RRTeam"}
        # tag_2 = {"Key": "AppID", "Value": AppID}
        tag_3 = {"Key": "owner", "Value": "HTC_RRTeam"}
        tag_4 = {"Key": "Name", "Value": "HTC_RRTeam"}
        # tag_5=  {"Key": "aws:createdBy", "Value": USERID}
       
       
        # convert time string to datetime
        t1 = datetime.now()
        print('Start time:', t1.time())
        
        
        if spotFlag==False: 
          windata = '''
            <powershell>
            # load dynamic golden_user_data.ps1
            Copy-S3Object -BucketName vbs-ami-resources -Key installer/golden_user_data.ps1 -LocalFile C:\golden_user_data.ps1 -Region us-east-1
            powershell -executionpolicy unrestricted -File 'C:\\golden_user_data.ps1'
            </powershell>
            '''
          instance = ec2.run_instances(
              ImageId=AMI,
              InstanceType=INSTANCE_TYPE,
              KeyName=KEY_NAME,
              MaxCount=amount,
              MinCount=amount,
              UserData = windata,
              NetworkInterfaces=[{
              'SubnetId': ec2info['subnetID'],
              'DeviceIndex': 0,
              'AssociatePublicIpAddress': True,
              'Groups': [SecurityGroupId]
              }],
              IamInstanceProfile={
                              'Arn': ARN,
                          
                      },
              TagSpecifications=[{'ResourceType': 'instance',
                                'Tags': [tag_1,tag_3,tag_4]}],
              BlockDeviceMappings=BlockDeviceMappings
          )
          json_data =[]
          for instance_i in range(len(instance['Instances'])):
            BlockDeviceMappings= instance['Instances'][instance_i]['BlockDeviceMappings']
            ec2_resource = boto3.resource('ec2')
            for item in BlockDeviceMappings:
              volumeId=item['Ebs']['VolumeId']
              volume = ec2_resource.Volume(volumeId)
              tag = volume.create_tags(
                  Tags=[
                      {
                          'Key': "owner",
                          'Value': USERID
                      },
                  ]
              )

            instance_id = instance['Instances'][instance_i]['InstanceId']

    
            state='pending'
            publicIP=''
            launchtime=''
            publicDnsName=''
            while(state=='pending'):
              Myec2= ec2.describe_instances()
              for pythonins in Myec2['Reservations']:
                for printout in pythonins['Instances']:
                  if printout['InstanceId']==instance_id:
                    logger.info("============instance_data=============")
                    logger.info(printout)
                    if 'PublicIpAddress' in printout.keys():
                      state='done'

                      publicIP=printout['PublicIpAddress']
                      publicDnsName=printout['PublicDnsName']
                      launchtime=printout['LaunchTime'].strftime("%Y-%m-%d,%H:%M:%S")
            logger.info("============Ip Done=============") 
            
            response=dynamodb.put_item(TableName='VBS_Instances_Information', Item={
            'id':{'S':instance_id},
            'publicIP':{'S':publicIP},
            'appStatus':{'S':""},
            'region':{'S':REGION},
            'zone':{'S':ZONE},
            'userid':{'S':USERID},
            'instancetype':{'S':INSTANCE_TYPE},
            'launchtime':{'S':launchtime},
            'stoppedtime':{'S':""},
            'publicDnsName':{'S':publicDnsName}
            
          })
            response=dynamodb.put_item(TableName='VBS_Instance_Pool', Item={
            'instanceId':{'S':instance_id},
            'instanceIp':{'S':publicIP},
            'region':{'S':REGION},
            'zone':{'S':ZONE},
            'userId':{'S':USERID},
            'instanceStatus':{'S':'running'},
            'eventId':{'S':eventId},
            'eventTime':{'S':eventTime},
            'available':{'S':'true'},
            'gsi_zone':{'S':ZONE},
           
            
          })
          
            json_data.append({
                          "status":"success",
                          "instance_id": instance_id, 
                          "instance_region": REGION,
                          "instance_ip":publicIP,
                          "instance_zone": ZONE,
                          "instance_type": INSTANCE_TYPE,
                          'userid':USERID,
                          'publicDnsName':publicDnsName
                          
                          })
            logger.info("============ json_data     =============")
            logger.info(json_data)
          return json_data        
        
        
        else:
          logger.info("Spot")
          ec2_source = boto3.resource('ec2')
          InstanceMarketOptions={
          'MarketType': 'spot',
          'SpotOptions': {
              'MaxPrice':'50',
              'SpotInstanceType': 'one-time',
              'BlockDurationMinutes': 123,
              'ValidUntil': datetime(2015, 1, 1),
              'InstanceInterruptionBehavior': 'stop'
              }
         },
          
          instance = ec2_source.create_instances(
          BlockDeviceMappings=BlockDeviceMappings,
          ImageId=AMI,
          InstanceType=INSTANCE_TYPE,
          KeyName=KEY_NAME,
          IamInstanceProfile={
                              'Arn': ARN
                      },
          TagSpecifications=[{'ResourceType': 'instance',
                                'Tags': [tag_1,tag_3,tag_4]}],
          
          NetworkInterfaces=[{
              'SubnetId': ec2info['subnetID'],
              'DeviceIndex': 0,
              'AssociatePublicIpAddress': True,
              'Groups': [SecurityGroupId]
              }],
          
          
          InstanceMarketOptions= InstanceMarketOptions,
         
          )    
          instance_id = instance['Instances'][0]['InstanceId']
       
  
          state='pending'
          publicIP=''
          launchtime=''
          publicDnsName=''
          while(state=='pending'):
            Myec2= ec2.describe_instances()
            for pythonins in Myec2['Reservations']:
              for printout in pythonins['Instances']:
                if printout['InstanceId']==instance_id:
                  logger.info("============instance_data=============")
                  logger.info(printout)
                  if 'PublicIpAddress' in printout.keys():
                    state='done'
                  
                    publicIP=printout['PublicIpAddress']
                    publicDnsName=printout['PublicDnsName']
                    launchtime=printout['LaunchTime'].strftime("%Y-%m-%d,%H:%M:%S")
          logger.info("============Ip Done=============") 
          
          response=dynamodb.put_item(TableName='VBS_Instances_Information', Item={
          'id':{'S':instance_id},
          'publicIP':{'S':publicIP},
          
          'region':{'S':REGION},
          'zone':{'S':ZONE},
          'userid':{'S':USERID},
          'instancetype':{'S':INSTANCE_TYPE},
          'launchtime':{'S':launchtime},
          'publicDnsName':{'S':publicDnsName}
          
        })
          
          json_data = [{
                          "status":"success",
                          "instance_id": instance_id, 
                          "instance_region": REGION,
                          "instance_ip":publicIP,
                          "instance_zone": ZONE,
                          "instance_type": INSTANCE_TYPE,
                          'userid':USERID,
                          'publicDnsName':publicDnsName
                          
                        }]
          logger.info("============ json_data     =============")
          logger.info(json_data)
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
    