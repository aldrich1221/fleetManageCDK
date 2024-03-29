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
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
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

          ///////////////////////// Layers ////////////////////////
          const layer1 = new lambda.LayerVersion(this, 'ip_analysis_layer', {
            compatibleRuntimes: [
              lambda.Runtime.PYTHON_3_8,
              lambda.Runtime.PYTHON_3_9,
            ],
            code: lambda.Code.fromAsset(path.join(__dirname,'../../src/layers','ip_analysis.zip')),
            description: 'multiplies a number by 2',
          });
          ////////////////////////////////////// user usage table///////////////////////////
          const table2 = new dynamodb.Table(this, 'Table2', { 
            tableName:'VBS_User_UsageAndCost',
            partitionKey: { name: 'eventId', type: dynamodb.AttributeType.STRING }, 
            billingMode: dynamodb.BillingMode.PROVISIONED, 
            readCapacity: 20,
            writeCapacity: 20,
            removalPolicy: cdk.RemovalPolicy.DESTROY,
            sortKey: {name: 'datetime', type: dynamodb.AttributeType.STRING},
            pointInTimeRecovery: true,
            tableClass: dynamodb.TableClass.STANDARD,
          });
    
          table2.addGlobalSecondaryIndex({
            indexName: 'userId_datetime_index',
            partitionKey: {name: 'userId', type: dynamodb.AttributeType.STRING},
            sortKey: {name: 'datetime', type: dynamodb.AttributeType.STRING},
            readCapacity: 1,
            writeCapacity: 1,
            projectionType: dynamodb.ProjectionType.ALL,
          });



      /////////////////////////////////////   Queue  ///////////////////////////
      const queue = new  sqs.Queue(this, 'VBS_Cloud_MessageQueue', {
        queueName: 'VBS_Cloud_MessageQueue',
        visibilityTimeout:Duration.seconds(1200),
        receiveMessageWaitTime:Duration.seconds(0)
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
    //   const Function_vbs_message_consumer = new lambda.DockerImageFunction(this, 'Function_vbs_message_consumer',{
    //     functionName: 'Function_vbs_message_consumer',
    //     code: lambda.DockerImageCode.fromImageAsset(path.join(__dirname, '../../src/consumer'), {
    //     cmd: [ "app.lambda_handler" ],
      
       
    //     }),
    //     timeout: Duration.seconds(30),
    // });

    const Function_vbs_message_consumer = new lambda.Function(this, 'Function_vbs_message_consumer', {
      runtime: lambda.Runtime.PYTHON_3_8,
      handler: 'app.lambda_handler',
      code: lambda.Code.fromAsset(path.join(__dirname, '../../src/consumer')),
      functionName:'Function_vbs_message_consumer',
      timeout: Duration.seconds(900),
      layers:[layer1]
    });

      const Policy_vbs_message_consumer = new iam.PolicyStatement();
      Policy_vbs_message_consumer.addResources("*");
      Policy_vbs_message_consumer.addActions("*");
      Function_vbs_message_consumer.addToRolePolicy(Policy_vbs_message_consumer);
    
      // 👇 add sqs queue as event source for lambda
      Function_vbs_message_consumer.addEventSource(
        new SqsEventSource(queue, {
          batchSize: 1,
          maxBatchingWindow:Duration.seconds(5),
          reportBatchItemFailures:true,
          
        }),
      );


       const Function_vbs_api_authorize = new lambda.DockerImageFunction(this, 'Function_vbs_api_authorize',{
      functionName: 'Function_vbs_api_authorize_basic_instancePool',
      code: lambda.DockerImageCode.fromImageAsset(path.join(__dirname, '../../src/apiAuth'), {
      cmd: [ "app.lambda_handler" ],
      }),
      timeout: Duration.seconds(30),
    });
    

   /////////////////////////////////////   producer:attach_ec2  ///////////////////////////
  //   const Function_vbs_attach_ec2 = new lambda.DockerImageFunction(this, 'Function_vbs_attach_ec2',{
  //     functionName: 'Function_vbs_attach_ec2',
  //     code: lambda.DockerImageCode.fromImageAsset(path.join(__dirname, '../../src/attachEC2'), {
  //     cmd: [ "app.lambda_handler" ],
        
     
  //     }),
  //     timeout: Duration.seconds(900),
  // });


  const Function_vbs_attach_ec2 = new lambda.Function(this, 'Function_vbs_attach_ec2', {
    runtime: lambda.Runtime.PYTHON_3_8,
    handler: 'app.lambda_handler',
    code: lambda.Code.fromAsset(path.join(__dirname, '../../src/attachEC2')),
    functionName:'Function_vbs_attach_ec2',
    timeout: Duration.seconds(900),
    layers:[layer1]
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



  //   /////////////////////////////////////   producer:detach_ec2  ///////////////////////////
  //   const Function_vbs_detach_ec2 = new lambda.DockerImageFunction(this, 'Function_vbs_detach_ec2',{
  //     functionName: 'Function_vbs_detach_ec2',
  //     code: lambda.DockerImageCode.fromImageAsset(path.join(__dirname, '../../src/detachEC2'), {
  //     cmd: [ "app.lambda_handler" ],
    
     
  //     }),
  //     timeout: Duration.seconds(900),
  // });


  const Function_vbs_detach_ec2 = new lambda.Function(this, 'Function_vbs_detach_ec2', {
    runtime: lambda.Runtime.PYTHON_3_8,
    handler: 'app.lambda_handler',
    code: lambda.Code.fromAsset(path.join(__dirname, '../../src/detachEC2')),
    functionName:'Function_vbs_detach_ec2',
    timeout: Duration.seconds(900),
    layers:[layer1]
  });

    const Policy_vbs_detach_ec2 = new iam.PolicyStatement();
    Policy_vbs_detach_ec2.addResources("*");
    Policy_vbs_detach_ec2.addActions("*");
    Function_vbs_detach_ec2.addToRolePolicy(Policy_vbs_detach_ec2);
    const API_vbs_detach_ec2=new apigateway.LambdaRestApi(this, 'API_vbs_detach_ec2', {
      handler: Function_vbs_detach_ec2,
      restApiName:'API_vbs_detach_ec2',
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

    const API_vbs_detach_ec2_v1 = API_vbs_detach_ec2.root.addResource('v1');
    const API_vbs_detach_ec2_user = API_vbs_detach_ec2_v1.addResource('user');
    const API_vbs_detach_ec2_userid = API_vbs_detach_ec2_user.addResource('{userid}');
    
    
    const Authorizer_vbs_detach_ec2 = new apigateway.RequestAuthorizer(this, 'Authorizer_vbs_detach_ec2', {
      handler: Function_vbs_api_authorize,
      identitySources: [apigateway.IdentitySource.header('authorizationtoken')]
    });
    API_vbs_detach_ec2_userid.addMethod('POST',
    new apigateway.LambdaIntegration(Function_vbs_detach_ec2, {proxy: true}), {
      authorizer: Authorizer_vbs_detach_ec2
    });


    const Function_vbs_create_ec2_emergency = new lambda.DockerImageFunction(this, 'Function_vbs_create_ec2_emergency',{
      functionName: 'Function_vbs_create_ec2_emergency',
      code: lambda.DockerImageCode.fromImageAsset(path.join(__dirname, '../../src/createEC2Emergency'), {
      cmd: [ "app.lambda_handler" ],
      }),
      timeout: Duration.seconds(600),
  });
    const Policy_vbs_create_ec2_emergency = new iam.PolicyStatement();
    Policy_vbs_create_ec2_emergency .addResources("*");
    Policy_vbs_create_ec2_emergency .addActions("*");
    Function_vbs_create_ec2_emergency .addToRolePolicy(Policy_vbs_create_ec2_emergency);
  
    
    //////////////////////////////////Monitor and Cost ////////////////////////
    // const Function_vbs_monitor_pool = new lambda.Function(this, 'FUNCTION_vbs_monitor_pool', {
    //   runtime: lambda.Runtime.PYTHON_3_8,
    //   handler: 'app.lambda_handler',
    //   code: lambda.Code.fromAsset(path.join(__dirname,'../../src/monitorAndCost')),
    //   functionName:'FUNCTION_vbs_monitor_pool'
    // });

    const Function_vbs_monitor_pool = new lambda.Function(this, 'Function_vbs_monitor_pool', {
      runtime: lambda.Runtime.PYTHON_3_8,
      handler: 'app.lambda_handler',
      code: lambda.Code.fromAsset(path.join(__dirname, '../../src/monitorAndCost')),
      functionName:'Function_vbs_monitor_pool',
      timeout: Duration.seconds(600),
      layers:[layer1]
    });




    const Policy_vbs_monitor_pool = new iam.PolicyStatement();
    Policy_vbs_monitor_pool.addResources("*");
    Policy_vbs_monitor_pool.addActions("*");
    Function_vbs_monitor_pool.addToRolePolicy(Policy_vbs_monitor_pool); 
    const API_vbs_monitor_pool = new apigateway.LambdaRestApi(this, 'API_vbs_monitor_pool', {
      handler: Function_vbs_monitor_pool,
      restApiName:'API_vbs_monitor_pool',
      proxy: false,
      integrationOptions: {
        allowTestInvoke: false,
          timeout: Duration.seconds(5),
        },
      defaultCorsPreflightOptions: { allowOrigins: apigateway.Cors.ALL_ORIGINS },
    });
    const API_vbs_monitor_pool_v1 = API_vbs_monitor_pool.root.addResource('v1');

    // API_vbs_unit_Test_v1.addMethod('GET',
    // new apigateway.LambdaIntegration(Function_vbs_unit_Test, {proxy: true}));

    const Authorizer_vbs_monitor_pool = new apigateway.RequestAuthorizer(this, 'Authorizer_vbs_monitor_pool', {
      handler: Function_vbs_api_authorize,
      identitySources: [apigateway.IdentitySource.header('authorizationtoken')]
    });
    
    API_vbs_monitor_pool_v1.addMethod('POST',
    new apigateway.LambdaIntegration(Function_vbs_monitor_pool, {proxy: true}), {
      authorizer: Authorizer_vbs_monitor_pool
    });
 
    
    ////////////////////////////////// unit Test ///////////////////////////
    const Function_vbs_unit_Test = new lambda.Function(this, 'Function_vbs_unit_Test', {
      runtime: lambda.Runtime.PYTHON_3_8,
      handler: 'app.lambda_handler',
      code: lambda.Code.fromAsset(path.join(__dirname,'../../testing/unitTest')),
      functionName:'Function_vbs_unit_Test'
    });
    const Policy_vbs_unit_Test = new iam.PolicyStatement();
    Policy_vbs_unit_Test.addResources("*");
    Policy_vbs_unit_Test.addActions("*");
    Function_vbs_unit_Test.addToRolePolicy(Policy_vbs_unit_Test); 
    const API_vbs_unit_Test = new apigateway.LambdaRestApi(this, 'API_vbs_unit_Test', {
      handler: Function_vbs_unit_Test,
      restApiName:'API_vbs_unit_Test',
      proxy: false,
      integrationOptions: {
        allowTestInvoke: false,
          timeout: Duration.seconds(5),
        },
      defaultCorsPreflightOptions: { allowOrigins: apigateway.Cors.ALL_ORIGINS },
    });
    const API_vbs_unit_Test_v1 = API_vbs_unit_Test.root.addResource('v1');

    // API_vbs_unit_Test_v1.addMethod('GET',
    // new apigateway.LambdaIntegration(Function_vbs_unit_Test, {proxy: true}));

    const Authorizer_vbs_unit_Test = new apigateway.RequestAuthorizer(this, 'Authorizer_vbs_unit_Test', {
      handler: Function_vbs_api_authorize,
      identitySources: [apigateway.IdentitySource.header('authorizationtoken')]
    });

    API_vbs_unit_Test_v1.addMethod('POST',
    new apigateway.LambdaIntegration(Function_vbs_unit_Test, {proxy: true}), {
      authorizer: Authorizer_vbs_unit_Test
    });


    ////////////////////////////////////////// integration test //////////////////////////////
    const Function_vbs_integration_test = new lambda.Function(this, 'Function_vbs_integration_test', {
      runtime: lambda.Runtime.PYTHON_3_8,
      handler: 'app.lambda_handler',
      code: lambda.Code.fromAsset(path.join(__dirname,'../../testing/integrationTest')),
      functionName:'Function_vbs_integration_test',
      timeout: Duration.seconds(600),
      layers:[layer1]
    });
    const Policy_vbs_integration_test = new iam.PolicyStatement();
    Policy_vbs_integration_test.addResources("*");
    Policy_vbs_integration_test.addActions("*");
    Function_vbs_integration_test.addToRolePolicy(Policy_vbs_integration_test); 
    const API_vbs_integration_test = new apigateway.LambdaRestApi(this, 'API_vbs_integration_test', {
      handler: Function_vbs_integration_test,
      restApiName:'API_vbs_integration_test',
      proxy: false,
      integrationOptions: {
        allowTestInvoke: false,
          timeout: Duration.seconds(5),
        },
      defaultCorsPreflightOptions: { allowOrigins: apigateway.Cors.ALL_ORIGINS },
    });
    const API_vbs_integration_test_v1 = API_vbs_integration_test.root.addResource('v1');

    // API_vbs_unit_Test_v1.addMethod('GET',
    // new apigateway.LambdaIntegration(Function_vbs_unit_Test, {proxy: true}));

    const Authorizer_vbs_integration_test = new apigateway.RequestAuthorizer(this, 'Authorizer_vbs_integration_test', {
      handler: Function_vbs_api_authorize,
      identitySources: [apigateway.IdentitySource.header('authorizationtoken')]
    });

    API_vbs_integration_test_v1.addMethod('POST',
    new apigateway.LambdaIntegration(Function_vbs_integration_test, {proxy: true}), {
      authorizer: Authorizer_vbs_integration_test
    });


    ///////////////////////////////////////Cost calucalation ////////////////////////////////////////

    const Function_vbs_cost_calculation = new lambda.Function(this, 'Function_vbs_cost_calculation', {
      runtime: lambda.Runtime.PYTHON_3_8,
      handler: 'app.lambda_handler',
      code: lambda.Code.fromAsset(path.join(__dirname,'../../src/costCalculateDynamoDB')),
      functionName:'Function_vbs_cost_calculation',
      timeout: Duration.seconds(600),
      layers:[layer1]
    });

    const Policy_vbs_cost_calculation = new iam.PolicyStatement();
    Policy_vbs_cost_calculation.addResources("*");
    Policy_vbs_cost_calculation.addActions("*");
    Function_vbs_cost_calculation.addToRolePolicy(Policy_vbs_cost_calculation); 
    const API_vbs_cost_calculation = new apigateway.LambdaRestApi(this, 'API_vbs_cost_calculation', {
      handler: Function_vbs_cost_calculation,
      restApiName:'API_vbs_cost_calculation',
      proxy: false,
      integrationOptions: {
        allowTestInvoke: false,
          timeout: Duration.seconds(29),
        },
      defaultCorsPreflightOptions: { allowOrigins: apigateway.Cors.ALL_ORIGINS },
    });
    const API_vbs_cost_calculation_v1 = API_vbs_cost_calculation.root.addResource('v1');
   
    const API_vbs_cost_calculation_user = API_vbs_cost_calculation_v1.addResource('user');
    const API_vbs_cost_calculation_userid = API_vbs_cost_calculation_user.addResource('{userid}');
    const API_vbs_cost_calculation_action = API_vbs_cost_calculation_userid.addResource('action');
    const API_vbs_cost_calculation_actionid = API_vbs_cost_calculation_action.addResource('{actionid}');

    // API_vbs_unit_Test_v1.addMethod('GET',
    // new apigateway.LambdaIntegration(Function_vbs_unit_Test, {proxy: true}));

    const Authorizer_vbs_cost_calculation = new apigateway.RequestAuthorizer(this, 'Authorizer_vbs_cost_calculation', {
      handler: Function_vbs_api_authorize,
      identitySources: [apigateway.IdentitySource.header('authorizationtoken')]
    });

    API_vbs_cost_calculation_actionid.addMethod('POST',
    new apigateway.LambdaIntegration(Function_vbs_cost_calculation, {proxy: true}), {
      authorizer: Authorizer_vbs_cost_calculation
    });


  



  }
}
