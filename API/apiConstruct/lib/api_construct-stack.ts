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
export class ApiConstructStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    //#1 API Authorize //////////////////////////////
    const Function_vbs_api_authorize = new lambda.DockerImageFunction(this, 'Function_vbs_api_authorize',{
      functionName: 'Function_vbs_api_authorize',
      code: lambda.DockerImageCode.fromImageAsset(path.join(__dirname, '../../src/apiAuth'), {
      cmd: [ "app.lambda_handler" ],
      }),
      timeout: Duration.seconds(900),
    });

    //#2 API test //////////////////////////////
    const Function_vbs_test = new lambda.DockerImageFunction(this, 'Function_vbs_test',{
        functionName: 'Function_vbs_test',
        code: lambda.DockerImageCode.fromImageAsset(path.join(__dirname, '../../src/test'), {
        cmd: [ "app.lambda_handler" ],
        }),
        timeout: Duration.seconds(900),
    });
    
    const API_vbs_test=new apigateway.LambdaRestApi(this, 'API_vbs_test', {
      handler: Function_vbs_test,
      restApiName:'API_vbs_test',
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
    
    const Authorizer_vbs_test = new apigateway.RequestAuthorizer(this, 'Authorizer_vbs_test', {
      handler: Function_vbs_api_authorize,
      identitySources: [apigateway.IdentitySource.header('authorizationtoken')]
    });
    
    const API_vbs_test_v1 = API_vbs_test.root.addResource('v1');
    API_vbs_test_v1.addMethod('GET',
    new apigateway.LambdaIntegration(Function_vbs_test, {proxy: true}), {
      authorizer: Authorizer_vbs_test
    });
    
    API_vbs_test_v1.addMethod('POST',
    new apigateway.LambdaIntegration(Function_vbs_test, {proxy: true}), {
      authorizer: Authorizer_vbs_test
    });
    API_vbs_test_v1.addMethod('PUT',
    new apigateway.LambdaIntegration(Function_vbs_test, {proxy: true}), {
      authorizer: Authorizer_vbs_test
    });

    
    //#3 API issue handle //////////////////////////////
    const Function_vbs_issue_handle = new lambda.DockerImageFunction(this, 'Function_vbs_issue_handle',{
      functionName: 'Function_vbs_issue_handle',
      code: lambda.DockerImageCode.fromImageAsset(path.join(__dirname, '../../src/ec2rescue'), {
      cmd: [ "app.lambda_handler" ],
    
     
      }),
      timeout: Duration.seconds(900),
  });

    const Policy_vbs_issue_handle = new iam.PolicyStatement();
    Policy_vbs_issue_handle.addResources("*");
    Policy_vbs_issue_handle.addActions("*");
    Function_vbs_issue_handle.addToRolePolicy(Policy_vbs_issue_handle);
    const API_vbs_issue_handle=new apigateway.LambdaRestApi(this, 'API_vbs_issue_handle', {
      handler: Function_vbs_issue_handle,
      restApiName:'API_vbs_issue_handle',
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

    const API_vbs_issue_handle_v1 = API_vbs_issue_handle.root.addResource('v1');
    const API_vbs_issue_handle_user = API_vbs_issue_handle_v1.addResource('user');
    const API_vbs_issue_handle_userid = API_vbs_issue_handle_user.addResource('{userid}');
    
    const API_vbs_issue_handle_ec2 = API_vbs_issue_handle_userid.addResource("ec2")
    const API_vbs_issue_handle_ec2id = API_vbs_issue_handle_ec2.addResource('{ec2id}')

    const Authorizer_vbs_issue_handle = new apigateway.RequestAuthorizer(this, 'Authorizer_vbs_issue_handle', {
      handler: Function_vbs_api_authorize,
      identitySources: [apigateway.IdentitySource.header('authorizationtoken')]
    });
    API_vbs_issue_handle_ec2id.addMethod('POST',
    new apigateway.LambdaIntegration(Function_vbs_issue_handle, {proxy: true}), {
      authorizer: Authorizer_vbs_issue_handle
    });

    // const UsagePlan_API_vbs_issue_handle = API_vbs_issue_handle.addUsagePlan('UsagePlan', {
    //   name: 'UsagePlan_API_vbs_issue_handle',
    //   throttle: {
    //     rateLimit: 10,
    //     burstLimit: 10
    //   }
    // });
  
    // const Key_vbs_issue_handle=API_vbs_issue_handle.addApiKey(`developer_apikey-API_vbs_issue_handle`, {
    //   apiKeyName: `developer_apikey-API_vbs_issue_handle`,
    //   value:"abcdefghijk123456789"
    // }
    // )
    // UsagePlan_API_vbs_issue_handle.addApiKey(Key_vbs_issue_handle);

    //#4 Iam //////////////////////////////

  

    const Function_vbs_create_iam_user = new lambda.DockerImageFunction(this, 'Function_vbs_create_iam_user',{
      functionName: 'Function_vbs_create_iam_user',
      code: lambda.DockerImageCode.fromImageAsset(path.join(__dirname, '../../src/iamManage'), {
      cmd: [ "app.lambda_handler" ],
      }),
      timeout: Duration.seconds(900),
  });
    const Policy_vbs_create_iam_user = new iam.PolicyStatement();
    Policy_vbs_create_iam_user.addResources("*");
    Policy_vbs_create_iam_user.addActions("*");
    Function_vbs_create_iam_user.addToRolePolicy(Policy_vbs_create_iam_user);

    const eventRule=new events.Rule(this, "Rule", {
    
      schedule:events.Schedule.rate(cdk.Duration.days(20))
    });

    eventRule.addTarget(
      new targets.LambdaFunction(Function_vbs_create_iam_user, {
        event: events.RuleTargetInput.fromObject({ message: "Hello Lambda" }),
      })
    );

    targets.addLambdaPermission(eventRule, Function_vbs_create_iam_user);



    
    ///////////life Cycle
    const Function_vbs_lifecycle_manage = new lambda.DockerImageFunction(this, 'Function_vbs_lifecycle_manage',{
      functionName: 'Function_vbs_lifecycle_manage',
      code: lambda.DockerImageCode.fromImageAsset(path.join(__dirname, '../../src/lifeCycleCost'), {
      cmd: [ "app.lambda_handler" ],
      }),
      timeout: Duration.seconds(900),
  });
    const Policy_vbs_lifecycle_manage = new iam.PolicyStatement();
    Policy_vbs_lifecycle_manage.addResources("*");
    Policy_vbs_lifecycle_manage.addActions("*");
    Function_vbs_lifecycle_manage.addToRolePolicy(Policy_vbs_lifecycle_manage);

    const eventRule_vbs_lifecycle_manage=new events.Rule(this, "twentyDaysRule", {
    
      schedule:events.Schedule.rate(cdk.Duration.minutes(5))
    });

    eventRule_vbs_lifecycle_manage.addTarget(
      new targets.LambdaFunction(Function_vbs_lifecycle_manage, {
        event: events.RuleTargetInput.fromObject({ message: "Hello Lambda" }),
      })
    );

    targets.addLambdaPermission(eventRule_vbs_lifecycle_manage, Function_vbs_lifecycle_manage);


    //////////////# Network ###############
    const Function_vbs_network_analysis = new lambda.DockerImageFunction(this, 'Function_vbs_network_analysis',{
      functionName: 'Function_vbs_network_analysis',
      code: lambda.DockerImageCode.fromImageAsset(path.join(__dirname, '../../src/network'), {
      cmd: [ "app.lambda_handler" ],
    
     
      }),
      timeout: Duration.seconds(900),
  });

    const Policy_vbs_network_analysis = new iam.PolicyStatement();
    Policy_vbs_network_analysis.addResources("*");
    Policy_vbs_network_analysis.addActions("*");
    Function_vbs_network_analysis.addToRolePolicy(Policy_vbs_network_analysis);
    const API_vbs_network_analysis=new apigateway.LambdaRestApi(this, 'API_vbs_network_analysis', {
      handler: Function_vbs_network_analysis,
      restApiName:'API_vbs_network_analysis',
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

    const API_vbs_network_analysis_v1 = API_vbs_network_analysis.root.addResource('v1');
    const API_vbs_network_analysis_user = API_vbs_network_analysis_v1.addResource('user');
    const API_vbs_network_analysis_userid = API_vbs_network_analysis_user.addResource('{userid}');
    
    // const API_vbs_network_analysis_ec2 = API_vbs_network_analysis_userid.addResource("ec2")
    // const API_vbs_network_analysis_ec2id = API_vbs_network_analysis_ec2.addResource('{ec2id}')

    const Authorizer_vbs_network_analysis = new apigateway.RequestAuthorizer(this, 'Authorizer_vbs_network_analysis', {
      handler: Function_vbs_api_authorize,
      identitySources: [apigateway.IdentitySource.header('authorizationtoken')]
    });
    API_vbs_network_analysis_userid.addMethod('POST',
    new apigateway.LambdaIntegration(Function_vbs_network_analysis, {proxy: true}), {
      authorizer: Authorizer_vbs_network_analysis
    });


    ///////
    const Function_vbs_latency_test = new lambda.DockerImageFunction(this, 'Function_vbs_latency_test',{
      functionName: 'Function_vbs_latency_test',
      code: lambda.DockerImageCode.fromImageAsset(path.join(__dirname, '../../src/latencyTest'), {
      cmd: [ "app.lambda_handler" ],
    
     
      }),
      timeout: Duration.seconds(900),
  });

    const Policy_vbs_latency_test = new iam.PolicyStatement();
    Policy_vbs_latency_test.addResources("*");
    Policy_vbs_latency_test.addActions("*");
    Function_vbs_latency_test.addToRolePolicy(Policy_vbs_latency_test);
    const API_vbs_latency_test=new apigateway.LambdaRestApi(this, 'API_vbs_latency_test', {
      handler: Function_vbs_latency_test,
      // handler:Function_vbs_test,
      restApiName:'API_vbs_latency_test',
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

    const API_vbs_latency_test_v1 = API_vbs_latency_test.root.addResource('v1');
    const API_vbs_latency_test_user = API_vbs_latency_test_v1.addResource('user');
    const API_vbs_latency_test_userid = API_vbs_latency_test_user.addResource('{userid}');
    
    const API_vbs_latency_test_action = API_vbs_latency_test_userid.addResource("action")
    const API_vbs_latency_test_actionid = API_vbs_latency_test_action.addResource('{actionid}')

    
    const Authorizer_vbs_latency_test = new apigateway.RequestAuthorizer(this, 'Authorizer_vbs_latency_test', {
      handler: Function_vbs_api_authorize,
      identitySources: [apigateway.IdentitySource.header('authorizationtoken')]
    });
    API_vbs_latency_test_actionid.addMethod('POST',
    new apigateway.LambdaIntegration(Function_vbs_latency_test, {proxy: true}), {
      authorizer: Authorizer_vbs_latency_test
    });

    API_vbs_latency_test_actionid.addMethod('PUT',
    new apigateway.LambdaIntegration(Function_vbs_latency_test, {proxy: true}), {
      authorizer: Authorizer_vbs_latency_test
    });
    
    API_vbs_latency_test_actionid.addMethod('GET',
    new apigateway.LambdaIntegration(Function_vbs_latency_test, {proxy: true}), {
      authorizer: Authorizer_vbs_latency_test
    });

    


  
  
  }
}
