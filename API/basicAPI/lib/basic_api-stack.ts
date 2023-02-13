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

export class BasicApiStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);


    //////////////////  Layers ///////////////////////
    const layer1 = new lambda.LayerVersion(this, 'ip_analysis_layer', {
      compatibleRuntimes: [
        lambda.Runtime.PYTHON_3_8,
        lambda.Runtime.PYTHON_3_9,
      ],
      code: lambda.Code.fromAsset(path.join(__dirname,'../../src/layers','ip_analysis.zip')),
      description: 'multiplies a number by 2',
    });
    //////////#API Auth////////////
    const Function_vbs_api_authorize = new lambda.DockerImageFunction(this, 'Function_vbs_api_authorize',{
      functionName: 'Function_vbs_api_authorize_basic',
      code: lambda.DockerImageCode.fromImageAsset(path.join(__dirname, '../../src/apiAuth'), {
      cmd: [ "app.lambda_handler" ],
      }),
      timeout: Duration.seconds(900),
    });
    
    ///////////////////Create EC2////////////////

    //Method1 With Docker Image
  //   const Function_vbs_create_ec2 = new lambda.DockerImageFunction(this, 'Function_vbs_create_ec2',{
  //     functionName: 'Function_vbs_create_ec2',
  //     code: lambda.DockerImageCode.fromImageAsset(path.join(__dirname, '../../src/createEC2'), {
  //     cmd: [ "app.lambda_handler" ],
    
     
  //     }),
  //     timeout: Duration.seconds(900),
  // });

    ///Method2: with layers and zip 
    const Function_vbs_create_ec2 = new lambda.Function(this, 'Function_vbs_create_ec2', {
      runtime: lambda.Runtime.PYTHON_3_8,
      handler: 'app.lambda_handler',
      code: lambda.Code.fromAsset(path.join(__dirname, '../../src/createEC2')),
      functionName:'Function_vbs_create_ec2',
      timeout: Duration.seconds(600),
      layers:[layer1]
    });


    const Policy_vbs_create_ec2 = new iam.PolicyStatement();
    Policy_vbs_create_ec2.addResources("*");
    Policy_vbs_create_ec2.addActions("*");
    Function_vbs_create_ec2.addToRolePolicy(Policy_vbs_create_ec2);
    const API_vbs_create_ec2=new apigateway.LambdaRestApi(this, 'API_vbs_create_ec2', {
      handler: Function_vbs_create_ec2,
      restApiName:'API_vbs_create_ec2',
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

    const API_vbs_create_ec2_v1 = API_vbs_create_ec2.root.addResource('v1');
    const API_vbs_create_ec2_user = API_vbs_create_ec2_v1.addResource('user');
    const API_vbs_create_ec2_userid = API_vbs_create_ec2_user.addResource('{userid}');
    
 

    const Authorizer_vbs_create_ec2 = new apigateway.RequestAuthorizer(this, 'Authorizer_vbs_create_ec2', {
      handler: Function_vbs_api_authorize,
      identitySources: [apigateway.IdentitySource.header('authorizationtoken')]
    });
    API_vbs_create_ec2_userid.addMethod('POST',
    new apigateway.LambdaIntegration(Function_vbs_create_ec2, {proxy: true}), {
      authorizer: Authorizer_vbs_create_ec2
    });

    ///////////////////Manage EC2////////////////
    const Function_vbs_manage_ec2 = new lambda.DockerImageFunction(this, 'Function_vbs_manage_ec2',{
      functionName: 'Function_vbs_manage_ec2',
      code: lambda.DockerImageCode.fromImageAsset(path.join(__dirname, '../../src/manageEC2'), {
      cmd: [ "app.lambda_handler" ],
    
     
      }),
      timeout: Duration.seconds(900),
  });

    const Policy_vbs_manage_ec2 = new iam.PolicyStatement();
    Policy_vbs_manage_ec2.addResources("*");
    Policy_vbs_manage_ec2.addActions("*");
    Function_vbs_manage_ec2.addToRolePolicy(Policy_vbs_manage_ec2);
    const API_vbs_manage_ec2=new apigateway.LambdaRestApi(this, 'API_vbs_manage_ec2', {
      handler: Function_vbs_manage_ec2,
      restApiName:'API_vbs_manage_ec2',
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
          'authorizationToken',
        ],
        allowOrigins: apigateway.Cors.ALL_ORIGINS },
      integrationOptions: {
      allowTestInvoke: false,
        timeout: Duration.seconds(29),
      }
    });

    const API_vbs_manage_ec2_v1 = API_vbs_manage_ec2.root.addResource('v1');
    const API_vbs_manage_ec2_user = API_vbs_manage_ec2_v1.addResource('user');
    const API_vbs_manage_ec2_userid = API_vbs_manage_ec2_user.addResource('{userid}');
    const API_vbs_manage_ec2_action = API_vbs_manage_ec2_userid.addResource('action');
    const API_vbs_manage_ec2_actionid = API_vbs_manage_ec2_action.addResource('{actionid}');
    
 

    const Authorizer_vbs_manage_ec2 = new apigateway.RequestAuthorizer(this, 'Authorizer_vbs_manage_ec2', {
      handler: Function_vbs_api_authorize,
      identitySources: [apigateway.IdentitySource.header('authorizationtoken')]
    });
    API_vbs_manage_ec2_actionid.addMethod('POST',
    new apigateway.LambdaIntegration(Function_vbs_manage_ec2, {proxy: true}), {
      authorizer: Authorizer_vbs_manage_ec2
    });



    ////////////////////////Query DB//////////////////////////
    const Function_vbs_query_db = new lambda.DockerImageFunction(this, 'Function_vbs_query_db',{
      functionName: 'Function_vbs_query_db',
      code: lambda.DockerImageCode.fromImageAsset(path.join(__dirname, '../../src/queryDB'), {
      cmd: [ "app.lambda_handler" ],
    
     
      }),
      timeout: Duration.seconds(900),
  });

    const Policy_vbs_query_db = new iam.PolicyStatement();
    Policy_vbs_query_db.addResources("*");
    Policy_vbs_query_db.addActions("*");
    Function_vbs_query_db.addToRolePolicy(Policy_vbs_query_db);
    const API_vbs_query_db=new apigateway.LambdaRestApi(this, 'API_vbs_query_db', {
      handler: Function_vbs_query_db,
      restApiName:'API_vbs_query_db',
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
          'authorizationToken',
        ],
        allowOrigins: apigateway.Cors.ALL_ORIGINS },
      integrationOptions: {
      allowTestInvoke: false,
        timeout: Duration.seconds(29),
      }
    });

    const API_vbs_query_db_v1 = API_vbs_query_db.root.addResource('v1');
    const API_vbs_query_db_user = API_vbs_query_db_v1.addResource('user');
    const API_vbs_query_db_userid = API_vbs_query_db_user.addResource('{userid}');
    const API_vbs_query_db_table = API_vbs_query_db_userid.addResource('table');
    const API_vbs_query_db_tablename = API_vbs_query_db_table.addResource('{tablename}');
    const API_vbs_query_db_action = API_vbs_query_db_tablename.addResource('action');
    const API_vbs_query_db_actionid = API_vbs_query_db_action.addResource('{actionid}');
    
 

    const Authorizer_vbs_query_db = new apigateway.RequestAuthorizer(this, 'Authorizer_vbs_query_db', {
      handler: Function_vbs_api_authorize,
      identitySources: [apigateway.IdentitySource.header('authorizationtoken')]
    });
    API_vbs_query_db_actionid.addMethod('POST',
    new apigateway.LambdaIntegration(Function_vbs_query_db, {proxy: true}), {
      authorizer: Authorizer_vbs_query_db
    });

    /////////////////////////////////cost explorer
    const Function_vbs_cost = new lambda.DockerImageFunction(this, 'Function_vbs_cost',{
      functionName: 'Function_vbs_cost',
      code: lambda.DockerImageCode.fromImageAsset(path.join(__dirname, '../../src/costExplorer'), {
      cmd: [ "app.lambda_handler" ],
    
     
      }),
      timeout: Duration.seconds(900),
  });

    const Policy_vbs_cost = new iam.PolicyStatement();
    Policy_vbs_cost.addResources("*");
    Policy_vbs_cost.addActions("*");
    Function_vbs_cost.addToRolePolicy(Policy_vbs_cost);
    const API_vbs_cost=new apigateway.LambdaRestApi(this, 'API_vbs_cost', {
      handler: Function_vbs_cost,
      restApiName:'API_vbs_cost',
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
          'authorizationToken',
        ],
        allowOrigins: apigateway.Cors.ALL_ORIGINS },
      integrationOptions: {
      allowTestInvoke: false,
        timeout: Duration.seconds(29),
      }
    });

    const API_vbs_cost_v1 = API_vbs_cost.root.addResource('v1');
    const API_vbs_cost_user = API_vbs_cost_v1.addResource('user');
    const API_vbs_cost_userid = API_vbs_cost_user.addResource('{userid}');
    const API_vbs_cost_action = API_vbs_cost_userid.addResource('action');
    const API_vbs_cost_actionid = API_vbs_cost_action.addResource('{actionid}');
    
 

    const Authorizer_vbs_cost = new apigateway.RequestAuthorizer(this, 'Authorizer_vbs_cost', {
      handler: Function_vbs_api_authorize,
      identitySources: [apigateway.IdentitySource.header('authorizationtoken')]
    });
    API_vbs_cost_actionid.addMethod('POST',
    new apigateway.LambdaIntegration(Function_vbs_cost, {proxy: true}), {
      authorizer: Authorizer_vbs_cost
    });


  }
}
