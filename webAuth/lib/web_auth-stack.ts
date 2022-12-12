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

export class WebAuthStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    

    const Function_vbs_web_auth_login = new lambda.DockerImageFunction(this, 'Function_vbs_web_auth_login',{
      functionName: 'Function_vbs_web_auth_login',
      code: lambda.DockerImageCode.fromImageAsset(path.join(__dirname, '../src/sampleAuthLogin'), {
      cmd: [ "index.handler" ], 
      }),
      timeout: Duration.seconds(900),
  });
 
  const Policy_vbs_web_auth_login = new iam.PolicyStatement({
    resources: ['*'],
    actions: ['sts:AssumeRole'],
    effect: iam.Effect.ALLOW
  });
    // Policy_vbs_web_auth_login.addServicePrincipal('ec2.amazonaws.com');
    
    
    Policy_vbs_web_auth_login.addResources("*");
    Policy_vbs_web_auth_login.addActions("*");


    Function_vbs_web_auth_login.addToRolePolicy(Policy_vbs_web_auth_login);

    const API_vbs_web_auth_login=new apigateway.LambdaRestApi(this, 'API_vbs_web_auth_login', {
      handler: Function_vbs_web_auth_login,
      restApiName:'API_vbs_web_auth_login',
      proxy: false,
      apiKeySourceType:ApiKeySourceType.HEADER,
      defaultCorsPreflightOptions: { 
        allowHeaders: [
          'Content-Type',
          'X-Amz-Date',
          'Authorization',
          'X-Api-Key',
          'authorizationToken',
        ],
        allowOrigins: apigateway.Cors.ALL_ORIGINS },
      integrationOptions: {
      allowTestInvoke: false,
        timeout: Duration.seconds(29),
      }
    });
    
    const API_vbs_web_auth_login_v1 = API_vbs_web_auth_login.root.addResource('v1');
    API_vbs_web_auth_login_v1.addMethod('GET',
    new apigateway.LambdaIntegration(Function_vbs_web_auth_login, {proxy: true}), {
      
    });
    
    
  }
}
