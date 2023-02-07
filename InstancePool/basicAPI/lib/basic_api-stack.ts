import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
// import * as sqs from 'aws-cdk-lib/aws-sqs';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as tasks from 'aws-cdk-lib/aws-stepfunctions-tasks';
import * as stepFunc from 'aws-cdk-lib/aws-stepfunctions';
import { Duration, Stack, StackProps } from 'aws-cdk-lib';
import * as path from 'path';
import * as sqs from 'aws-cdk-lib/aws-sqs';
import { ApiKey, ApiKeySourceType } from 'aws-cdk-lib/aws-apigateway';

import * as iam from 'aws-cdk-lib/aws-iam';
import {SqsEventSource} from 'aws-cdk-lib/aws-lambda-event-sources';

import * as apigateway from 'aws-cdk-lib/aws-apigateway'

// declare const submitLambda: lambda.Function;
// declare const getStatusLambda: lambda.Function;

export class BasicApiStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    
//     const submitLambda = new lambda.DockerImageFunction(this, 'Function_vbs_test_step1',{
//       functionName: 'Function_vbs_test_step1',
//       code: lambda.DockerImageCode.fromImageAsset(path.join(__dirname, '../../src/test'), {
//       cmd: [ "app.lambda_handler" ],
//       }),
//       timeout: Duration.seconds(900),
//   });

//   const getStatusLambda = new lambda.DockerImageFunction(this, 'Function_vbs_test_step2',{
//     functionName: 'Function_vbs_test_step2',
//     code: lambda.DockerImageCode.fromImageAsset(path.join(__dirname, '../../src/test'), {
//     cmd: [ "app.lambda_handler" ],
//     }),
//     timeout: Duration.seconds(900),
// });

//     const submitJob = new tasks.LambdaInvoke(this, 'Submit Job', {
//       lambdaFunction: submitLambda,
//       // Lambda's result is in the attribute `Payload`
//       outputPath: '$.Payload',
//     });
    
//     const waitX = new stepFunc.Wait(this, 'Wait X Seconds', {
//       time: stepFunc.WaitTime.secondsPath('$.waitSeconds'),
//     });
    
//     const getStatus = new tasks.LambdaInvoke(this, 'Get Job Status', {
//       lambdaFunction: getStatusLambda,
//       // Pass just the field named "guid" into the Lambda, put the
//       // Lambda's result in a field called "status" in the response
//       inputPath: '$.guid',
//       outputPath: '$.Payload',
//     });
    
//     const jobFailed = new stepFunc.Fail(this, 'Job Failed', {
//       cause: 'AWS Batch Job Failed',
//       error: 'DescribeJob returned FAILED',
//     });
    
//     const finalStatus = new tasks.LambdaInvoke(this, 'Get Final Job Status', {
//       lambdaFunction: getStatusLambda,
//       // Use "guid" field as input
//       inputPath: '$.guid',
//       outputPath: '$.Payload',
//     });
    
//     const definition = submitJob
//       .next(waitX)
//       .next(getStatus)
//       .next(new stepFunc.Choice(this, 'Job Complete?')
//         // Look at the "status" field
//         .when(stepFunc.Condition.stringEquals('$.status', 'FAILED'), jobFailed)
//         .when(stepFunc.Condition.stringEquals('$.status', 'SUCCEEDED'), finalStatus)
//         .otherwise(waitX));
    
//     new stepFunc.StateMachine(this, 'StateMachine', {
//       definition,
      
//       timeout: Duration.minutes(5),
//     });

      // const queue = new sqs.Queue(this, 'sqs-queue');



      /////////////////////////////////////   Queue  ///////////////////////////
      const queue = new  sqs.Queue(this, 'VBS_Cloud_MessageQueue', {
        queueName: 'VBS_Cloud_MessageQueue',
      });

      const queueL1 = new  sqs.Queue(this, 'VBS_Cloud_MessageQueue_L1', {
        queueName: 'VBS_Cloud_MessageQueue_L1',
      });
      const queueL2 = new  sqs.Queue(this, 'VBS_Cloud_MessageQueue_L2', {
        queueName: 'VBS_Cloud_MessageQueue_L2',
      });
      const queueL3= new  sqs.Queue(this, 'VBS_Cloud_MessageQueue_L3', {
        queueName: 'VBS_Cloud_MessageQueue_L3',
      });
     
      /////////////////////////////////////   consumer  ///////////////////////////
      const Function_vbs_message_consumer = new lambda.DockerImageFunction(this, 'Function_vbs_message_consumer',{
        functionName: 'Function_vbs_message_consumer',
        code: lambda.DockerImageCode.fromImageAsset(path.join(__dirname, '../../src/consumer'), {
        cmd: [ "app.lambda_handler" ],
      
       
        }),
        timeout: Duration.seconds(30),
    });
      const Policy_vbs_message_consumer = new iam.PolicyStatement();
      Policy_vbs_message_consumer.addResources("*");
      Policy_vbs_message_consumer.addActions("*");
      Function_vbs_message_consumer.addToRolePolicy(Policy_vbs_message_consumer);
    
      // 👇 add sqs queue as event source for lambda
      Function_vbs_message_consumer.addEventSource(
        new SqsEventSource(queue, {
          batchSize: 1,
        }),
      );


       const Function_vbs_api_authorize = new lambda.DockerImageFunction(this, 'Function_vbs_api_authorize',{
      functionName: 'Function_vbs_api_authorize_basic',
      code: lambda.DockerImageCode.fromImageAsset(path.join(__dirname, '../../src/apiAuth'), {
      cmd: [ "app.lambda_handler" ],
      }),
      timeout: Duration.seconds(30),
    });
    
   /////////////////////////////////////   producer:attach_ec2  ///////////////////////////
    const Function_vbs_attach_ec2 = new lambda.DockerImageFunction(this, 'Function_vbs_attach_ec2',{
      functionName: 'Function_vbs_attach_ec2',
      code: lambda.DockerImageCode.fromImageAsset(path.join(__dirname, '../../src/attachEC2'), {
      cmd: [ "app.lambda_handler" ],
    
     
      }),
      timeout: Duration.seconds(900),
  });

    const Policy_vbs_attach_ec2 = new iam.PolicyStatement();
    Policy_vbs_attach_ec2.addResources("*");
    Policy_vbs_attach_ec2.addActions("*");
    Function_vbs_attach_ec2.addToRolePolicy(Policy_vbs_attach_ec2);
    const API_vbs_attach_ec2=new apigateway.LambdaRestApi(this, 'API_vbs_attach_ec2', {
      handler: Function_vbs_attach_ec2,
      restApiName:'API_vbs_attach_ec2',
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

    const API_vbs_attach_ec2_v1 = API_vbs_attach_ec2.root.addResource('v1');
    const API_vbs_attach_ec2_user = API_vbs_attach_ec2_v1.addResource('user');
    const API_vbs_attach_ec2_userid = API_vbs_attach_ec2_user.addResource('{userid}');
    const API_vbs_attach_ec2_region = API_vbs_attach_ec2_userid.addResource('region');
    const API_vbs_attach_ec2_regionid = API_vbs_attach_ec2_region.addResource('{regionid}');
    
    const Authorizer_vbs_attach_ec2 = new apigateway.RequestAuthorizer(this, 'Authorizer_vbs_attach_ec2', {
      handler: Function_vbs_api_authorize,
      identitySources: [apigateway.IdentitySource.header('authorizationtoken')]
    });
    API_vbs_attach_ec2_regionid.addMethod('POST',
    new apigateway.LambdaIntegration(Function_vbs_attach_ec2, {proxy: true}), {
      authorizer: Authorizer_vbs_attach_ec2
    });


    //////////////////////////// test ///////////////////
    
    const Function_vbs_test_pool = new lambda.DockerImageFunction(this, 'Function_vbs_test_pool',{
      functionName: 'Function_vbs_test_pool',
      code: lambda.DockerImageCode.fromImageAsset(path.join(__dirname, '../../src/test'), {
      cmd: [ "app.lambda_handler" ],
    
     
      }),
      timeout: Duration.seconds(900),
  });

    const Policy_vbs_test_pool = new iam.PolicyStatement();
    Policy_vbs_test_pool.addResources("*");
    Policy_vbs_test_pool.addActions("*");
    Function_vbs_test_pool.addToRolePolicy(Policy_vbs_test_pool);
    const API_vbs_test_pool=new apigateway.LambdaRestApi(this, 'API_vbs_test_pool', {
      handler: Function_vbs_test_pool,
      restApiName:'API_vbs_test_pool',
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

    const API_vbs_test_pool_v1 = API_vbs_test_pool.root.addResource('v1');
    
    
    const Authorizer_vbs_test_pool = new apigateway.RequestAuthorizer(this, 'Authorizer_vbs_test_pool', {
      handler: Function_vbs_api_authorize,
      identitySources: [apigateway.IdentitySource.header('authorizationtoken')]
    });
    API_vbs_test_pool_v1.addMethod('POST',
    new apigateway.LambdaIntegration(Function_vbs_test_pool, {proxy: true}), {
      authorizer: Authorizer_vbs_test_pool
    });


  }
}
