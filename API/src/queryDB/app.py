import re
import boto3
import json
import boto3
import logging
import boto3
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
            tableName=pathParameters['tablename']
            action=pathParameters['actionid']
    except:
        raise CustomError("Please check the parameters.")

    #########code here
    if tableName=='VBS_Instances_Information':
        dynamodb_resource = boto3.resource('dynamodb', region_name='us-east-1')

        
        table = dynamodb_resource.Table('VBS_Instances_Information')
        if action=='scanAll':
        
            response = table.scan(
            )
            item = response['Items']
    
        elif action=='scanByUser':
            try:
                userid=body["userid"]
                response = table.scan(
                            FilterExpression=Attr('userid').eq(userid)
                        
                        )
                item = response['Items']
                allData=[]
                for eachEC2 in item:
                    logger.info("eachEC2")
                    logger.info(eachEC2)
                    
                    instanceId=eachEC2['id']
                    region=eachEC2['region']
                    ec2 = boto3.client('ec2',region_name=region)
                    instance_status = ec2.describe_instance_status(
                                InstanceIds=[
                                    instanceId
                                ],
                            )
                    logger.info(instance_status)
                    if len(instance_status['InstanceStatuses'])>0:
                        eachEC2["state"]=instance_status['InstanceStatuses'][0]['InstanceState']['Name']
                        eachEC2["instanceStatus"]=instance_status['InstanceStatuses'][0]['InstanceStatus']['Status']
                        eachEC2["systemStatus"]=instance_status['InstanceStatuses'][0]['SystemStatus']['Status']
                    else:
                        eachEC2["state"]="Stopped"
                        eachEC2["instanceStatus"]="No Data"
                        eachEC2["systemStatus"]="No Data"
                    allData.append(eachEC2)
            
                json_data = [{
                                "status":"success",
                                "data":allData
                                }]
                logger.info("=========== Instance Table Response=============")
                logger.info(json_data)
                return json_data
            except:
                raise
    elif tableName=='VBS_Letency_Test':
        dynamodb_resource = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb_resource.Table('VBS_Letency_Test')
        if action=="scanByUser":
            try:
                userid=body["userid"]
                response = table.scan(
                        FilterExpression=Attr('user_id').eq(userid)
                    )
            
                item = response['Items']
                item = sorted(item, key=lambda k: k['latency'], reverse=False)
                
                logger.info("============latency test event Response=============")
                logger.info(query['userid'])
                logger.info(response)
                json_data = [{
                            "status":"success",
                            "latencyTest":item
                            }]
                return json_data
            except:
                raise
            
        elif action=="scanByCity":
            logger.info("============latency test by City=============")
            try:
                city=body["city"]
                response = table.scan(
                        FilterExpression=Attr('userCity').eq(city)
                    )
                logger.info(response)
                item = response['Items']
                json_data = [{
                            "status":"success",
                            "latencyTest":item
                            }]
                logger.info("============latency test event Response=============")
                logger.info(json_data)
                return json_data
            except:
                raise
               
        elif action=="scanByDeveloper":
            try:
                response = table.scan(
                    FilterExpression=Attr('user_id').eq("developer-123456789")
                )
                logger.info( response )
                item = response['Items']
                json_data = [{
                            "status":"success",
                            "latencyTest":item
                            }]
                return json_data
            except:
                raise
        elif action=="scanAll":
            try:
                response = table.scan(
                )
                item = response['Items']
                json_data = [{
                            "status":"success",
                            "latencyTest":item
                            }]
                return json_data
            except:
                raise
    elif tableName=='VBS_Enterprise_Info':
        dynamodb_resource = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb_resource.Table('VBS_Enterprise_Info')
        if action=='scanByUser':
            try:
                userid=body['userid']
                response = table.scan(
                        FilterExpression=Attr('userid').eq(userid)
                    )
                if len(response['Items'])>0:
                    item = response['Items'][0]
                    # item = sorted(item, key=lambda k: k['latency'], reverse=False)
                    today = date.today()
                    d = today.strftime("%Y-%m-%d")
                    one_months = today + relativedelta(days=-7)
                    d2=one_months.strftime("%Y-%m-%d")
                    client_ce = boto3.client('ce')
                    result = client_ce.get_cost_and_usage(
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
                                query['userid'],
                            ],
                            'MatchOptions': ['EQUALS']
                        }
                    }
                    )
                    logger.info(item)
                    data={
                        "userid":item["userid"],
                        "instanceQuota":str(item['instanceQuota']),
                        "email":str(item['email']),
                        'username':str(item['username']),
                        "cost":result
                    }
                else:
                    client_ce = boto3.client('ce')
                    result = client_ce.get_cost_and_usage(
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
                                query['userid'],
                            ],
                            'MatchOptions': ['EQUALS']
                        }
                    }
                    )
                    data={
                        "userid":query['userid'],
                        "instanceQuota":str(10),
                        "cost":result
                    }
                logger.info("============latency test event Response=============")
                logger.info(query['userid'])
                logger.info(response)
                json_data = [{
                            "status":"success",
                            "userinfo":data
                            }]
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
    