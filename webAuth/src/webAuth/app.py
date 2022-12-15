import re
import boto3
import json
import boto3
import logging
import boto3
from boto3.dynamodb.conditions import Key, Attr

import sys, os, base64, datetime, hashlib, hmac 
import requests # pip install requests
import time
from uuid import uuid4
AccessControlAllowOrigin="https://d1wzk0972nk23y.cloudfront.net"
logger = logging.getLogger()
logger.setLevel(logging.INFO)
class CustomError(Exception):
  pass
def process(event, context):
    try:
            logger.info(event)
            body=event['body']
            # body= json.loads(body)
            pathParameters=event['pathParameters']
            headers=event['headers']
            query=event['queryStringParameters']
    except:
        raise CustomError("Please check the parameters.")

    #########code here
    # userid=headers['userid']
    # password=headers['password']
    userid=query['userid']
    password=query['password']

    ##########

    
    dynamodb_resource = boto3.resource('dynamodb', region_name='us-east-1')

        
    table = dynamodb_resource.Table('VBS_Enterprise_Info')
    response = table.scan(
                            FilterExpression=Attr('userid').eq(userid)
                        
                        )
    logger.info(response)
    item = response['Items'][0]
    if  item['userpassword']==password:
        dynamodb_resource = boto3.resource('dynamodb', region_name='us-east-1')

                
        table = dynamodb_resource.Table('VBS_Enterprise_Info')
        
        temp_credentials={}
        response = table.query(
        KeyConditionExpression=Key('userid').eq('Enterprise_User_Service')
        )
        if 'Items' in response.keys():
            item = response['Items'][0]
            
            sts_client = boto3.client(
                'sts', aws_access_key_id=item['keypair_id'], aws_secret_access_key=item['keypair_secret'])
            try:
                response_data={}
                session_name=f'enterpriseUser_session-{uuid4()}'
                apikey=item['apikey']
                response = sts_client.assume_role(
                    RoleArn=item['iam_role_arn'], RoleSessionName=session_name)
                temp_credentials = response['Credentials']
                logger.info("===========credential token------------")
                logger.info(temp_credentials)
                #############################################
                
                method = 'GET'
                service = 's3'
                host = 's3-website-us-east-1.amazonaws.com'
                region = 'us-east-1'
                endpoint = 'http://vbs-user-website-bucket-htc.s3-website-us-east-1.amazonaws.com/index.html'
                request_parameters = 'Action=DescribeRegions&Version=2013-10-15'

                # Key derivation functions. See:
                # http://docs.aws.amazon.com/general/latest/gr/signature-v4-examples.html#signature-v4-examples-python
                def sign(key, msg):
                    return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

                def getSignatureKey(key, dateStamp, regionName, serviceName):
                    kDate = sign(('AWS4' + key).encode('utf-8'), dateStamp)
                    kRegion = sign(kDate, regionName)
                    kService = sign(kRegion, serviceName)
                    kSigning = sign(kService, 'aws4_request')
                    return kSigning

                # Read AWS access key from env. variables or configuration file. Best practice is NOT
                # to embed credentials in code.
                # access_key = os.environ.get('AWS_ACCESS_KEY_ID')
                # secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
                access_key =item['keypair_id']
                secret_key =item['keypair_secret']
             
                if access_key is None or secret_key is None:
                    print('No access key is available.')
                    sys.exit()

                # Create a date for headers and the credential string
                t = datetime.datetime.utcnow()
                amzdate = t.strftime('%Y%m%dT%H%M%SZ')
                datestamp = t.strftime('%Y%m%d') # Date w/o time, used in credential scope


                # ************* TASK 1: CREATE A CANONICAL REQUEST *************
                # http://docs.aws.amazon.com/general/latest/gr/sigv4-create-canonical-request.html

                # Step 1 is to define the verb (GET, POST, etc.)--already done.

                # Step 2: Create canonical URI--the part of the URI from domain to query 
                # string (use '/' if no path)
                canonical_uri = '/' 

                # Step 3: Create the canonical query string. In this example (a GET request),
                # request parameters are in the query string. Query string values must
                # be URL-encoded (space=%20). The parameters must be sorted by name.
                # For this example, the query string is pre-formatted in the request_parameters variable.
                logger.info("=========request_parameters===========")
                logger.info(request_parameters)
                canonical_querystring = request_parameters
                aldrichqueryString=request_parameters

                # Step 4: Create the canonical headers and signed headers. Header names
                # must be trimmed and lowercase, and sorted in code point order from
                # low to high. Note that there is a trailing \n.
                canonical_headers = 'host:' + host + '\n' + 'x-amz-date:' + amzdate + '\n'
                logger.info("=========canonical_headers===========")
                logger.info(canonical_headers)
                aldrichqueryString=aldrichqueryString+'&X-Amz-Date='+amzdate
                # Step 5: Create the list of signed headers. This lists the headers
                # in the canonical_headers list, delimited with ";" and in alpha order.
                # Note: The request can include any headers; canonical_headers and
                # signed_headers lists those that you want to be included in the 
                # hash of the request. "Host" and "x-amz-date" are always required.
                signed_headers = 'host;x-amz-date'
                aldrichqueryString=aldrichqueryString+'&X-Amz-SignedHeaders=host'
                # Step 6: Create payload hash (hash of the request body content). For GET
                # requests, the payload is an empty string ("").
                payload_hash = hashlib.sha256(('').encode('utf-8')).hexdigest()

                # Step 7: Combine elements to create canonical request
                canonical_request = method + '\n' + canonical_uri + '\n' + canonical_querystring + '\n' + canonical_headers + '\n' + signed_headers + '\n' + payload_hash


                logger.info("=========canonical_request===========")
                logger.info(canonical_request)
                # ************* TASK 2: CREATE THE STRING TO SIGN*************
                # Match the algorithm to the hashing algorithm you use, either SHA-1 or
                # SHA-256 (recommended)
                algorithm = 'AWS4-HMAC-SHA256'
                credential_scope = datestamp + '/' + region + '/' + service + '/' + 'aws4_request'
                string_to_sign = algorithm + '\n' +  amzdate + '\n' +  credential_scope + '\n' +  hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()

                logger.info("=========credential_scope===========")
                logger.info(credential_scope)
                logger.info("=========string_to_sign===========")
                logger.info(string_to_sign)

                # ************* TASK 3: CALCULATE THE SIGNATURE *************
                # Create the signing key using the function defined above.
                signing_key = getSignatureKey(secret_key, datestamp, region, service)
                logger.info("=========signing_key===========")
                logger.info(signing_key)


                # Sign the string_to_sign using the signing_key
                signature = hmac.new(signing_key, (string_to_sign).encode('utf-8'), hashlib.sha256).hexdigest()
                logger.info("=========signature===========")
                logger.info(signature)

                # ************* TASK 4: ADD SIGNING INFORMATION TO THE REQUEST *************
                # The signing information can be either in a query string value or in 
                # a header named Authorization. This code shows how to use a header.
                # Create authorization header and add to request headers
                authorization_header = algorithm + ' ' + 'Credential=' + access_key + '/' + credential_scope + ', ' +  'SignedHeaders=' + signed_headers + ', ' + 'Signature=' + signature
                
                # aldrichqueryString=aldrichqueryString+'&X-Amz-Algorithm='+algorithm+'&X-Amz-Credential='+ access_key + '/' + credential_scope +
                
                
                # The request can include any headers, but MUST include "host", "x-amz-date", 
                # and (for this scenario) "Authorization". "host" and "x-amz-date" must
                # be included in the canonical_headers and signed_headers, as noted
                # earlier. Order here is not significant.
                # Python note: The 'host' header is added automatically by the Python 'requests' library.
                headers = {'x-amz-date':amzdate, 'Authorization':authorization_header}


                logger.info("=========all headers===========")
                logger.info(headers)
                

                # ************* SEND THE REQUEST *************
                request_url = endpoint + '?' + canonical_querystring

                print('\nBEGIN REQUEST++++++++++++++++++++++++++++++++++++')
                print('Request URL = ' + request_url)
                r = requests.get(request_url, headers=headers)
        
                print('\nRESPONSE++++++++++++++++++++++++++++++++++++')
                print('Response code: %d\n' % r.status_code)
                print(r.text)
                
                
                #####################################

                s3_client = boto3.client('s3',region_name='us-east-1',
                          aws_access_key_id=access_key,
                          aws_secret_access_key=secret_key)

                expiration=3600
                response_presigned = s3_client.generate_presigned_url('get_object',
                                                            Params={'Bucket': 'vbs-user-website-bucket-htc',
                                                                    'Key': "index.html"},
                                                            ExpiresIn=expiration)
                logger.info("========S3 presigned------")
                logger.info(response_presigned)
                
                
                
                
                
                
                
                
                
                response_data["AccessKeyId"]=temp_credentials["AccessKeyId"],
                response_data["SecretAccessKey"]=temp_credentials["SecretAccessKey"],
                response_data["SessionToken"]=temp_credentials['SessionToken']
                response_data["PreSigned"]=response_presigned

                
                response_data["login"]=True
                response_data["apikey"]=apikey





            except:
                raise
        return response_data

    else:
        return {'login':False}
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
    