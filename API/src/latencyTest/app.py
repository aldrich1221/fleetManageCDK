import boto3
import json
import boto3
import logging
import boto3

import boto3, json, os, time
from boto3.dynamodb.conditions import Key, Attr
import geocoder
import logging
import requests
# import uuid
import time

# import sys

# from dateutil import parser



AccessControlAllowOrigin="https://d1wzk0972nk23y.cloudfront.net"
# AccessControlAllowOrigin=["http://vbs-user-website-bucket-htc.s3-website-us-east-1.amazonaws.com","https://d1wzk0972nk23y.cloudfront.net"]
logger = logging.getLogger()
logger.setLevel(logging.INFO)
class CustomError(Exception):
  pass
def process(event, context):
    try:
        logger.info(event)
        if 'body' in event.keys():
            body=event['body']
            if body!=None:
                body= json.loads(body)
        
        # source_ip=event['requestContext']['identity']['sourceIp']
        
        ##Rest
        pathParameters=event['pathParameters']
        userid=pathParameters['userid']
        action=pathParameters['actionid']
        source_ip=body['source_ip']
        # query=event['queryStringParameters']
        # userid=query['userid']
        # action=query['actionid']
        if action=='init':
            try:
                
                logger.info("============get user ip info=============")
                logger.info(source_ip)
                g = geocoder.ip(source_ip)
                logger.info(g)
                source_latitude=g.latlng[0]
                source_longitude=g.latlng[1]
                source_city=g.city
                
                # zones = [query['ec2zones']]
                # region=query['ec2region']
                logger.info("============get region info=============")
                
                dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

                
                choose_region=["ap-northeast-1",'sa-east-1']
                table = dynamodb.Table('VBS_Region_Info')
                response = table.scan(
                                FilterExpression=Attr("region").is_in(choose_region)
                            )
                
                logger.info("============region info response=============")
                logger.info(response)


                    
                user_data = '''#!/bin/bash
                nohup python -m SimpleHTTPServer &
                export ec2ip=$(curl "http://169.254.169.254/latest/meta-data/public-ipv4")
                sudo caddy reverse-proxy --from $ec2ip.nip.io --to localhost:8000
                '''
                    
                testKeyPair={
                    'us-east-1':'VBS-keypair-us-east-1',
                    'ap-east-1':'VBS-keypair-ap-east-1',
                    'ap-northeast-1':'VBS-keypair-ap-northeast-1',
                    'sa-east-1':'VBS-keypair-sa-east-1'
                
                }
                SecurityGroup={
                    'us-east-1':'sg-0f57bac64d35ab3c6',
                    'ap-east-1':'sg-0c52990d77152710a',
                    'ap-northeast-1':'sg-0277beebdbf92c2ae',
                    'sa-east-1':'sg-005b9e7b851a92948'
                    
                }
                AMI={
                    'us-east-1':'ami-0b81168cf55e3f4aa',
                    "ap-east-1":"ami-0e17f9d86aa4cae39",
                    "ap-northeast-1":"ami-06256127f1121ef5e",
                    'sa-east-1':'ami-0a4d919a117e184b1'
                
                }
                logger.info("============create instance=============")
                
                testInstances=[]
                for item in response['Items']:
                    try:
                        logger.info("============item['region']=============")
                        logger.info(item['region'])
                        if item['region'] not in choose_region:
                            continue
                        ec2 = boto3.client('ec2', region_name=item['region'])
                    
                        dynamodbClient = boto3.client('dynamodb')
                        instance = ec2.run_instances(
                            # ImageId=source_image['ImageId'],
                            ImageId=AMI[item['region']],
                            InstanceType='t3.medium',
                            KeyName=item['keypairName'],
                            # KeyName=testKeyPair[item['region']],
                            MaxCount=1,
                            MinCount=1,
                            UserData = user_data,
                            NetworkInterfaces=[{
                            'SubnetId': item['subnetID'],
                            'DeviceIndex': 0,
                            'AssociatePublicIpAddress': True,
                            'Groups': [SecurityGroup[item['region']]]
                        }],
                            
                        )
                        instance_id = instance['Instances'][0]['InstanceId']
                        testInstances.append(
                            { "ec2id":instance_id,
                                "ec2region":item['region'],
                                "ec2zone":item['zone']
                                }
                            )
                    except Exception as e:
                        
                        logger.info("============Can't launch=============")
                        logger.info(item['region'])
                        logger.info(e)
                
                ResponseInstanceData=[]
                for item in testInstances:
                    ec2 = boto3.client('ec2', region_name=item['ec2region'])
                    state='pending'
                    publicIP=''
                    publicDnsName=''
                    launchtime=''
                    while(state=='pending'):
                        Myec2= ec2.describe_instances()
                        for pythonins in Myec2['Reservations']:
                            for printout in pythonins['Instances']:
                                if printout['InstanceId']==item['ec2id']:
                                    logger.info("============instance_data=============")
                                    logger.info(printout)
                                    if 'PublicIpAddress' in printout.keys():
                                        state='done'
                        
                                        publicIP=printout['PublicIpAddress']
                                        publicDnsName=printout['PublicDnsName']
                            #   launchtime=printout['LaunchTime'].strftime("%Y-%m-%d,%H:%M:%S")
                    
                    
                
                    g2 = geocoder.ip(publicIP)
                    ec2_latitude=g2.latlng[0]
                    ec2_longitude=g2.latlng[1]
                    ec2_city=g2.city
                    ec2_country=g2.country
                    
                    eachitem={
                    'user_id': str(userid),
                    'instanceid':item['ec2id'],
                    'userIP':str(source_ip),
                    'userLatitude':str(source_latitude),
                    'userLongitude':str(source_longitude),
                    'userCity':str(source_city),
                    'instanceIP':str(publicIP),
                    'publicDnsName':str(publicDnsName),
                    'instanceLatitude':str(ec2_latitude),
                    'instanceLongitude':str(ec2_longitude),
                    'instanceCity':ec2_city,
                    'instanceCountry':ec2_country,
                    'latency':'',
                    'region':str(item['ec2region']),
                    'zone':str(item['ec2zone']),
                    'status_testEC2':'IPDone'
                    }
                    # response=dynamodbClient.put_item(TableName='VBS_Letency_Test', Item=
                    # {
                    # 'user_id':{'S' : str(userid)},
                    # 'instanceid':{'S':item['ec2id']},
                    # 'userIP':{'S':str(source_ip)},
                    # 'userLatitude':{'S':str(source_latitude)},
                    # 'userLongitude':{'S':str(source_longitude)},
                    # 'userCity':{'S':str(source_city)},
                    # 'instanceIP':{'S':publicIP},
                    # 'instanceLatitude':{'S':str(ec2_latitude)},
                    # 'instanceLongitude':{'S':str(ec2_longitude)},
                    # 'instanceCity':{'S':ec2_city},
                    # 'instanceCountry':{'S':ec2_country},
                    # 'latency':{'S':''},
                    # 'region':{'S':item['ec2region']},
                    # 'zone':{'S':item['ec2zone']},
                    # 'status_testEC2':{'S':'IPDone'}
                    # })
                    ResponseInstanceData.append(eachitem)
                
                
                json_data = [{'user_id': userid, 
                                'userIP':str(source_ip),
                                'userCity':{'S':str(source_city)},
                                "instanceData":ResponseInstanceData
                                }]
                logger.info("============json_data=============")
                logger.info(json_data)
                return json_data
            
            except:
                raise

        elif action=='check':
            InstanceData=body["instanceData"]
            instance_statuslist=[]
            for item in InstanceData:
                logger.info("============item=============")
                logger.info(item)
                # instanceidlist.append(item["instanceid"])
                ec2 = boto3.client('ec2', region_name=item['region'])
                instance_status = ec2.describe_instance_status(
                        InstanceIds=[item["instanceid"]]
                        )
                instance_statuslist.append(instance_status)
            json_data = [{'user_id': userid, 
                                'userIP':item['userIP'],
                              
                                "instanceData":instance_statuslist
                }]
            return json_data
        elif action=='delete': 
            InstanceData=body["instanceData"]
            instance_statuslist=[]
            for item in InstanceData:
                logger.info("============item=============")
                logger.info(item)
                # instanceidlist.append(item["instanceid"])
                ec2 = boto3.client('ec2', region_name=item['region'])
                instance_status = ec2.terminate_instances(
                        InstanceIds=[item["instanceid"]]
                        )
                instance_statuslist.append(instance_status)
                json_data = [{'user_id': userid, 
                                'userIP':item['userIP'],
                                "instanceData":instance_statuslist}]

            return json_data

            logger.info()
    except Exception as e:
        logger.info(e)
        raise CustomError("Please check the parameters.")

    #########code here
    
    ###########code here
    return "good"
def lambda_handler(event, context):
    try:
        if ('body' in event.keys()) & ('pathParameters' in event.keys()):

                data=process(event, context)
                logger.info("============data=============")
                logger.info(data)
                json_data = [{
                                "status":"success",
                                "data":data
                            
                              }]
                                
                logger.info("============success response=============")
                logger.info( json_data)
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