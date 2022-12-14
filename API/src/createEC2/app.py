import re
import boto3
import json

import logging

import os
from boto3.dynamodb.conditions import Key, Attr
import logging
from datetime import datetime
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
    USERID=pathParameters['userid']
    DEFAULTREGION = os.environ['AWS_REGION'] 
    INSTANCE_TYPE = body['ec2type']
    ZONE=body['ec2zone']
    appids=body['appids']
    userAMI=body['userAMI']
    spotFlag=body['spot']

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
      if userAMI=='withsteam':
        AMI=ec2info['AMI_withsteam']
      else:
        AMI=ec2info['AMI_withoutsteam']
      KEY_NAME=ec2info['keypairName']
      REGION=ec2info['region']
      ARN='arn:aws:iam::867217160264:instance-profile/VBSEC2InstanceProfile'
  
      ec2 = boto3.client('ec2', region_name=REGION)
      
      
      # if 'appid' in query.keys():
      if True:
        table_content = dynamodb_resource.Table('aldrichtest')
        logger.info("============table_content=============")
        BlockDeviceMappings=[{'DeviceName': '/dev/sda1',
                      'Ebs': {
                          'DeleteOnTermination': True,
                          'VolumeSize': 150,
                          
                      },}]
        deviceName=['xvda','xvdb','xvdc','xvdd','xvde','xvdf','xvdg','xvdh','xvdi','xvdj','xvdk','xvdl','xvdm','xvdn','xvdo','xvdp','xvdq','xvdr','xvds','xvdt','xvdu','xvdv','xvdw','xvdx','xvdy','xvdz']
        blocki=0
        for appid in appids:
          contentData = table_content.scan(
                      FilterExpression=Attr("appid").eq(str(appid))
                     
                  )
        
          logger.info(contentData)
          for item in contentData['Items']:
            if item['region']==REGION:
              EBSID=item['volid']      
              AppID=item['appid']
              BlockDeviceMappings.append(
                  {
                      'DeviceName': deviceName[blocki],
                      'Ebs': {
                          'DeleteOnTermination': True,
                          'SnapshotId': EBSID,
                          'VolumeSize': 150,
                          'Encrypted': True
                      },
                   
                  }
                )      
              blocki=blocki+1
              
              
        tag_1 = {"Key": "UserID", "Value": USERID}
        # tag_2 = {"Key": "AppID", "Value": AppID}
        tag_3 = {"Key": "owner", "Value": USERID}
        tag_4 = {"Key": "Name", "Value": USERID}
        # tag_5=  {"Key": "aws:createdBy", "Value": USERID}
       
       
        # convert time string to datetime
        t1 = datetime.now()
        print('Start time:', t1.time())
        
        
        if spotFlag==False: 
          windata = '''
            <script>  
            curl "http://169.254.169.254/latest/meta-data/public-ipv4" >> ec2ip.txt
            curl "http://169.254.169.254/latest/meta-data/instance-id" >> ec2id.txt
            curl "http://169.254.169.254/latest/meta-data/placement/region" >> region.txt
            set /p ec2ip=< ec2ip.txt
            set /p ec2id=< ec2id.txt
            set /p region=< region.txt
            </script> 
            <persist>true</persist>
            '''
          instance = ec2.run_instances(
              ImageId=AMI,
              InstanceType=INSTANCE_TYPE,
              KeyName=KEY_NAME,
              MaxCount=1,
              MinCount=1,
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
    