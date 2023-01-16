import { Duration, Stack, StackProps } from 'aws-cdk-lib';
import * as sns from 'aws-cdk-lib/aws-sns';
import * as subs from 'aws-cdk-lib/aws-sns-subscriptions';
import * as sqs from 'aws-cdk-lib/aws-sqs';
import { Construct } from 'constructs';

import * as iam from 'aws-cdk-lib/aws-iam';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as apig from 'aws-cdk-lib/aws-apigatewayv2';
import * as apigateway from 'aws-cdk-lib/aws-apigateway'
import * as path from 'path';
import { ApiKey, ApiKeySourceType } from 'aws-cdk-lib/aws-apigateway';
import * as resourcegroups from 'aws-cdk-lib/aws-resourcegroups';
import * as cdk from 'aws-cdk-lib';
import * as events from "aws-cdk-lib/aws-events";
import * as targets from "aws-cdk-lib/aws-events-targets";
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import { DockerImageAsset } from 'aws-cdk-lib/aws-ecr-assets';

export class ContentStatusStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

     //////////#API Auth////////////
     const Function_vbs_api_authorize = new lambda.DockerImageFunction(this, 'Function_vbs_api_authorize',{
      functionName: 'Function_vbs_api_authorize_appStatus',
      code: lambda.DockerImageCode.fromImageAsset(path.join(__dirname, '../../src/apiAuth'), {
      cmd: [ "app.lambda_handler" ],
      }),
      timeout: Duration.seconds(900),
    });



    /////////////////////updateAPIStatus////////////////////
    const Function_vbs_update_appStatus = new lambda.DockerImageFunction(this, 'Function_vbs_update_appStatus',{
      functionName: 'Function_vbs_update_appStatus',
      code: lambda.DockerImageCode.fromImageAsset(path.join(__dirname, '../../src/appStatus'), {
      cmd: [ "app.lambda_handler" ],
    
     
      }),
      timeout: Duration.seconds(900),
  });

    const Policy_vbs_update_appStatus = new iam.PolicyStatement();
    Policy_vbs_update_appStatus.addResources("*");
    Policy_vbs_update_appStatus.addActions("*");
    Function_vbs_update_appStatus.addToRolePolicy(Policy_vbs_update_appStatus);
    const API_vbs_update_appStatus=new apigateway.LambdaRestApi(this, 'API_vbs_update_appStatus', {
      handler: Function_vbs_update_appStatus,
      restApiName:'API_vbs_update_appStatus',
      proxy: false,
      apiKeySourceType:ApiKeySourceType.HEADER,
      defaultCorsPreflightOptions: { 
        allowHeaders: [
          'Content-Type',
          'X-Amz-Date',
          'authorization',
          'Authorization',
          'X-Api-Key',
          'authorizationtoken',
          'authorizationToken'
        ],
        allowOrigins: apigateway.Cors.ALL_ORIGINS },
      integrationOptions: {
      allowTestInvoke: false,
        timeout: Duration.seconds(29),
      }
    });

    
    const API_vbs_update_appStatus_v1 = API_vbs_update_appStatus.root.addResource('v1');
    const API_vbs_update_appStatus_tablename = API_vbs_update_appStatus_v1.addResource('tablename');
    const API_vbs_update_appStatus_tablenameid = API_vbs_update_appStatus_tablename.addResource('{tablename}');
    const API_vbs_update_appStatus_action = API_vbs_update_appStatus_tablenameid.addResource('action');
    const API_vbs_update_appStatus_actionid = API_vbs_update_appStatus_action.addResource('{actionid}');
    
 

    const Authorizer_vbs_update_appStatus = new apigateway.RequestAuthorizer(this, 'Authorizer_vbs_update_appStatus', {
      handler: Function_vbs_api_authorize,
      identitySources: [apigateway.IdentitySource.header('authorizationtoken')]
    });
    API_vbs_update_appStatus_actionid.addMethod('POST',
    new apigateway.LambdaIntegration(Function_vbs_update_appStatus, {proxy: true}), {
      authorizer: Authorizer_vbs_update_appStatus
    });


  }
}
