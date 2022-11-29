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
class CustomError(Exception):
  pass

def process(event, context):
    try: 
        try:
            logger.info(event)
            body=event['body']
            body= json.loads(body)
            pathParameters=event['pathParameters']
            action=pathParameters['action']
            userid=pathParameters['userid']
        except:
            raise CustomError("Please check the parameters.")
        
        data=[]    
        ec2=boto3.client('ec2')
        for iec2 in range(len(body["ec2ids"])):
            ec2id=body["ec2ids"][iec2]
            region=body["regions"][iec2]
            if action=='create_flow_logs':
                response_ec2_describe_instances=ec2.describe_instances(InstanceIds=[
                                    ec2id,
                                ])
                
                vpcid= response_ec2_describe_instances['Reservations'][0]['Instances'][0]['VpcId']
                subnetid= response_ec2_describe_instances['Reservations'][0]['Instances'][0]['SubnetId']
                networkinterfacesid= response_ec2_describe_instances['Reservations'][0]['Instances'][0]['NetworkInterfaces'][0]['NetworkInterfaceId']
                
                flowlogs=[]
                response1 = ec2.create_flow_logs(
                    TrafficType='ALL',
                    ResourceIds=[
                        vpcid,
                    ],
                    LogDestinationType='s3',
                    LogDestination='arn:aws:s3:::vbs-tempfile-bucket/'+ec2id,
                    ResourceType='VPC'
                    # LogFormat='${version} ${vpc-id} ${subnet-id} ${az-id} ${instance-id} ${srcaddr} ${dstaddr} ${srcport} ${dstport} ${protocol} ${tcp-flags} ${type} ${pkt-srcaddr} ${pkt-dstaddr} ${traffic-path}',
                )
                flowlogs.append(response1)
                response2 = ec2.create_flow_logs(
                    TrafficType='ALL',
                    LogDestinationType='s3',
                    LogDestination='arn:aws:s3:::vbs-tempfile-bucket/'+ec2id,
                    ResourceIds=[
                        subnetid,
                    ],
                    # LogFormat='${version} ${vpc-id} ${subnet-id} ${az-id} ${instance-id} ${srcaddr} ${dstaddr} ${srcport} ${dstport} ${protocol} ${tcp-flags} ${type} ${pkt-srcaddr} ${pkt-dstaddr} ${traffic-path}',
                    ResourceType='Subnet'
                )
                flowlogs.append(response2)
                response3 = ec2.create_flow_logs(
                    TrafficType='ALL',
                    ResourceIds=[
                        networkinterfacesid,
                    ],
                        LogFormat='${version} ${vpc-id} ${subnet-id} ${az-id} ${instance-id} ${srcaddr} ${dstaddr} ${srcport} ${dstport} ${protocol} ${tcp-flags} ${type} ${pkt-srcaddr} ${pkt-dstaddr} ${traffic-path}',
                    LogDestinationType='s3',
                    LogDestination='arn:aws:s3:::vbs-tempfile-bucket/'+ec2id,
                    ResourceType='NetworkInterface'
                )
                flowlogs.append(response3)
                
                newdata={
                        "label":"create_flow_logs",
                        "datapoints":[flowlogs]
                    }
                logger.info("============success response=============")
                logger.info(newdata)
                data.append(newdata)
                # data.append({'create_flow_logs':flowlogs})
            elif action=='get_flow_logs':
                FlowLogIds=body['flowLogIds']
                
                response = ec2.describe_flow_logs(
                    
                    FlowLogIds=FlowLogIds,
                    MaxResults=123,
                    NextToken='string'
                )
                s3path=response['FlowLogs'][0]['LogDestination']
            
            elif action=='delete_flow_logs':
                FlowLogIds=body['flowLogIds']
                logger.info("============delete_flow_logs=============")
                logger.info(FlowLogIds)
                
                response = ec2.delete_flow_logs(
                
                FlowLogIds=FlowLogIds
                
            )   
            
                logger.info("============success response=============")
                logger.info(response)
                data.append({
                "status":'success',
                "ec2id":ec2id,
                "data":response
            })
                
            
            logger.info("============success response=============")
                    # logger.info(result)
            logger.info(data)
                        
                 
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
            
            
