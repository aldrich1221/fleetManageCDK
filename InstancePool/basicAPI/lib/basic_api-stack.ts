import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
// import * as sqs from 'aws-cdk-lib/aws-sqs';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as tasks from 'aws-cdk-lib/aws-stepfunctions-tasks';
import * as stepFunc from 'aws-cdk-lib/aws-stepfunctions';
import { Duration, Stack, StackProps } from 'aws-cdk-lib';
import * as path from 'path';
// declare const submitLambda: lambda.Function;
// declare const getStatusLambda: lambda.Function;

export class BasicApiStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);


    const submitLambda = new lambda.DockerImageFunction(this, 'Function_vbs_test_step1',{
      functionName: 'Function_vbs_test_step1',
      code: lambda.DockerImageCode.fromImageAsset(path.join(__dirname, '../../src/test'), {
      cmd: [ "app.lambda_handler" ],
      }),
      timeout: Duration.seconds(900),
  });

  const getStatusLambda = new lambda.DockerImageFunction(this, 'Function_vbs_test_step2',{
    functionName: 'Function_vbs_test_step2',
    code: lambda.DockerImageCode.fromImageAsset(path.join(__dirname, '../../src/test'), {
    cmd: [ "app.lambda_handler" ],
    }),
    timeout: Duration.seconds(900),
});

    const submitJob = new tasks.LambdaInvoke(this, 'Submit Job', {
      lambdaFunction: submitLambda,
      // Lambda's result is in the attribute `Payload`
      outputPath: '$.Payload',
    });
    
    const waitX = new stepFunc.Wait(this, 'Wait X Seconds', {
      time: stepFunc.WaitTime.secondsPath('$.waitSeconds'),
    });
    
    const getStatus = new tasks.LambdaInvoke(this, 'Get Job Status', {
      lambdaFunction: getStatusLambda,
      // Pass just the field named "guid" into the Lambda, put the
      // Lambda's result in a field called "status" in the response
      inputPath: '$.guid',
      outputPath: '$.Payload',
    });
    
    const jobFailed = new stepFunc.Fail(this, 'Job Failed', {
      cause: 'AWS Batch Job Failed',
      error: 'DescribeJob returned FAILED',
    });
    
    const finalStatus = new tasks.LambdaInvoke(this, 'Get Final Job Status', {
      lambdaFunction: getStatusLambda,
      // Use "guid" field as input
      inputPath: '$.guid',
      outputPath: '$.Payload',
    });
    
    const definition = submitJob
      .next(waitX)
      .next(getStatus)
      .next(new stepFunc.Choice(this, 'Job Complete?')
        // Look at the "status" field
        .when(stepFunc.Condition.stringEquals('$.status', 'FAILED'), jobFailed)
        .when(stepFunc.Condition.stringEquals('$.status', 'SUCCEEDED'), finalStatus)
        .otherwise(waitX));
    
    new stepFunc.StateMachine(this, 'StateMachine', {
      definition,
      
      timeout: Duration.minutes(5),
    });
  }
}
