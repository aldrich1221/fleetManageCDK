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

export class UpdateDatabaseApiStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

   
    const Function_vbs_api_authorize = new lambda.DockerImageFunction(this, 'Function_vbs_api_authorize',{
      functionName: 'Function_vbs_api_authorize_update_database',
      code: lambda.DockerImageCode.fromImageAsset(path.join(__dirname, '../../src/apiAuth'), {
      cmd: [ "app.lambda_handler" ],
      }),
      timeout: Duration.seconds(900),
    });



    /////////////////////updateDatabaseAPI////////////////////
    const Function_vbs_update_database = new lambda.DockerImageFunction(this, 'Function_vbs_update_database',{
      functionName: 'Function_vbs_update_database',
      code: lambda.DockerImageCode.fromImageAsset(path.join(__dirname, '../../src/updateDB'), {
      cmd: [ "app.lambda_handler" ],
    
     
      }),
      timeout: Duration.seconds(900),
  });

    const Policy_vbs_update_database = new iam.PolicyStatement();
    Policy_vbs_update_database.addResources("*");
    Policy_vbs_update_database.addActions("*");
    Function_vbs_update_database.addToRolePolicy(Policy_vbs_update_database);
    const API_vbs_update_database=new apigateway.LambdaRestApi(this, 'API_vbs_update_database', {
      handler: Function_vbs_update_database,
      restApiName:'API_vbs_update_database',
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

    
    const API_vbs_update_database_v1 = API_vbs_update_database.root.addResource('v1');
    const API_vbs_update_database_tablename = API_vbs_update_database_v1.addResource('tablename');
    const API_vbs_update_database_tablenameid = API_vbs_update_database_tablename.addResource('{tablename}');
    const API_vbs_update_database_action = API_vbs_update_database_tablenameid.addResource('action');
    const API_vbs_update_database_actionid = API_vbs_update_database_action.addResource('{actionid}');
    
 

    const Authorizer_vbs_update_database = new apigateway.RequestAuthorizer(this, 'Authorizer_vbs_update_appStatus', {
      handler: Function_vbs_api_authorize,
      identitySources: [apigateway.IdentitySource.header('authorizationtoken')]
    });
    API_vbs_update_database_actionid.addMethod('POST',
    new apigateway.LambdaIntegration(Function_vbs_update_database, {proxy: true}), {
      authorizer: Authorizer_vbs_update_database
    });

  }
}
