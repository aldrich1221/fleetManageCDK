import json
import boto3
import logging
import boto3
import sys
from datetime import datetime, timedelta,date
from dateutil.relativedelta import relativedelta
from boto3.dynamodb.conditions import Key, Attr
from uuid import uuid4
logger = logging.getLogger()
logger.setLevel(logging.INFO)
AccessControlAllowOrigin="https://d1wzk0972nk23y.cloudfront.net"
CPUUtilization_threshold=11
class CustomError(Exception):
  pass

def list_s3_by_prefix(bucket, key_prefix, filter_func=None):
    s3=boto3.client('s3')
    next_token = ''
    all_keys = []
    while True:
        if next_token:
            res = s3.list_objects_v2(
                Bucket=bucket,
                ContinuationToken=next_token,
                Prefix=key_prefix)
            logger.info("============res=============")
            logger.info(res)
        else:
            res = s3.list_objects_v2(
                Bucket=bucket,
                Prefix=key_prefix)
            logger.info("============res=============")
            logger.info(res)
        if 'Contents' not in res:
            break

        if res['IsTruncated']:
            next_token = res['NextContinuationToken']
        else:
            next_token = ''

        if filter_func:
            keys = ["s3://{}/{}".format(bucket, item['Key']) for item in res['Contents'] if filter_func(item['Key'])]
        else:
            keys = ["s3://{}/{}".format(bucket, item['Key']) for item in res['Contents']]

        all_keys.extend(keys)

        logger.info("============all_keys=============")
        logger.info(all_keys)
        if not next_token:
            break
   
    print("find {} files in {}".format(len(all_keys), key_prefix))
    return all_keys
def process(event, context):
    try: 
        try:
            logger.info(event)
            body=event['body']
            body= json.loads(body)
            pathParameters=event['pathParameters']
            
            userid=pathParameters['userid']
        except:
            raise CustomError("Please check the parameters.")
        
        alldata=[]    
        ec2=boto3.client('ec2')
        for iec2 in range(len(body["ec2ids"])):
            ec2id=body["ec2ids"][iec2]
            action=body['action']
            region=body["regions"][iec2]
            data=[]    
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
                    LogDestination='arn:aws:s3:::vbs-tempfile-bucket-htc/'+ec2id,
                    ResourceType='VPC'
                    # LogFormat='${version} ${vpc-id} ${subnet-id} ${az-id} ${instance-id} ${srcaddr} ${dstaddr} ${srcport} ${dstport} ${protocol} ${tcp-flags} ${type} ${pkt-srcaddr} ${pkt-dstaddr} ${traffic-path}',
                )
                flowlogs.append(response1)
                response2 = ec2.create_flow_logs(
                    TrafficType='ALL',
                    LogDestinationType='s3',
                    LogDestination='arn:aws:s3:::vbs-tempfile-bucket-htc/'+ec2id,
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
                        # LogFormat='${version} ${vpc-id} ${subnet-id} ${az-id} ${instance-id} ${srcaddr} ${dstaddr} ${srcport} ${dstport} ${protocol} ${tcp-flags} ${type} ${pkt-srcaddr} ${pkt-dstaddr} ${traffic-path}',
                    LogDestinationType='s3',
                    LogDestination='arn:aws:s3:::vbs-tempfile-bucket-htc/'+ec2id,
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
                s3_source = boto3.resource('s3')
                FlowLogIds=body['flowLogIds']
                
                response = ec2.describe_flow_logs(
                    
                    FlowLogIds=FlowLogIds,
                   
                )
                logger.info("============success response=============")
                logger.info(response)
               
                s3path=response['FlowLogs'][0]['LogDestination']
                # ResourceId=response['FlowLogs'][i]['ResourceId']
                
                all_keys=list_s3_by_prefix('vbs-tempfile-bucket-htc',ec2id)
                allkeys=[]
                for i in range(len(all_keys)):
                    bucket, key = all_keys[0].split('/',2)[-1].split('/',1)
                    allkeys.append(key)
                obj = s3_source.Object(bucket, key)
                logger.info("============obj=============")
                logger.info(obj.get()['Body'].read())
                # txt=obj.get()['Body'].read().decode('utf-8') 
                # logger.info("============success response=============")
                # logger.info(txt)
                
                
                dynamodb_resource = boto3.resource('dynamodb', region_name='us-east-1')

                
                table = dynamodb_resource.Table('VBS_Enterprise_Info')
                
                
                response = table.query(
                KeyConditionExpression=Key('userid').eq('Enterprise_User_Service')
                )
                item = response['Items'][0]
               
                sts_client = boto3.client(
                        'sts', aws_access_key_id=item['keypair_id'], aws_secret_access_key=item['keypair_secret'])
                # sts_client = boto3.client(
                #         'sts', aws_access_key_id="AKIA4T2RLXBEA3M2SN4H", aws_secret_access_key="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")
                        
                session_name=f'enterpriseUser_session-{uuid4()}'
                response = sts_client.assume_role(
                    RoleArn=item['iam_role_arn'], RoleSessionName=session_name)
                    
                logger.info("============success response=============")
                logger.info(response)
                temp_credentials = response['Credentials']
                
                credentialData={
                "AccessKeyId": temp_credentials['AccessKeyId'],
                 "SecretAccessKey": temp_credentials['SecretAccessKey'],
                 'SessionToken':temp_credentials['SessionToken']
                 
                    
                }
                data.append({
                    'allkeys':allkeys,
                    'credentialData':credentialData

                })
            
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

            elif action=='network_insights_path':   
                    
                   
                desc=ec2.describe_instances(
                    InstanceIds=[
                        ec2id,
                    ],
                )
                vpcid=desc['Reservations'][0]['Instances'][0]['VpcId']
                
                responseIGW = ec2.describe_internet_gateways(
                    Filters=[
                        {
                            'Name': 'attachment.vpc-id',
                            'Values': [
                                vpcid,
                            ],
                        },
                    ],
                )
                
                igwid=responseIGW['InternetGateways'][0]['InternetGatewayId']
                
                response_insight_path=ec2.create_network_insights_path(
                    Source=igwid,
                    Destination=ec2id,
                    Protocol='tcp',
                    
                    )
                
                logger.info("============response_insight_path=============")
                logger.info(response_insight_path)  
                NetworkInsightsPathId=response_insight_path['NetworkInsightsPath']['NetworkInsightsPathId']
                
                result=ec2.start_network_insights_analysis(NetworkInsightsPathId=NetworkInsightsPathId)
                NetworkInsightsAnalysisId=result['NetworkInsightsAnalysis']['NetworkInsightsAnalysisId']
                
                
                result2=ec2.describe_network_insights_paths( NetworkInsightsPathIds=[NetworkInsightsPathId])
                paginator = ec2.get_paginator('describe_network_insights_analyses')
                
                pathAnlysisResult=None
                Flag=True
                while(Flag):
                    response_iterator = paginator.paginate(
                            NetworkInsightsAnalysisIds=[
                                NetworkInsightsAnalysisId,
                            ],
                            NetworkInsightsPathId=NetworkInsightsPathId,
                        
                        )
                    logger.info("============response_iterator=============")
                    logger.info(response_iterator)  
                    for page in response_iterator:
                        logger.info(page)  
                        
                        if page['NetworkInsightsAnalyses'][0]['Status']!='running':
                            Flag=False
                            page['NetworkInsightsAnalyses'][0]['ForwardPathComponents']
                            page['NetworkInsightsAnalyses'][0]['ReturnPathComponents']
                            
                            
                            pathAnlysisResult={
                                'ForwardPathComponents':page['NetworkInsightsAnalyses'][0]['ForwardPathComponents'],
                                'ReturnPathComponents':page['NetworkInsightsAnalyses'][0]['ReturnPathComponents'],
                                
                            }
                
                logger.info("============response_insight_path=============")
                # logger.info(result)
                logger.info(response_iterator )
                
                newdata={
                        "label":"network_insights_path",
                        "datapoints":[pathAnlysisResult]
                    }
                data.append(newdata)
                
                logger.info("============delete_network_insights_analysis=============")
                # logger.info(result)
                logger.info(NetworkInsightsAnalysisId )
                # data.append({'network_insights_path':pathAnlysisResult})
                response = ec2.delete_network_insights_analysis(
                    
                    NetworkInsightsAnalysisId=NetworkInsightsAnalysisId
                )
                ec2.delete_network_insights_path(NetworkInsightsPathId=NetworkInsightsPathId)
                        


            logger.info("============success response=============")
                    # logger.info(result)
            logger.info(data)
            alldata.append({
                    "status":'success',
                    "ec2id":ec2id,
                    "data":data
                })          
                 
        return alldata            
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
            
            
