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

export class SystemMonitorStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    // const queue = new sqs.Queue(this, 'SystemMonitorQueue', {
    //   visibilityTimeout: Duration.seconds(300)
    // });

    // const topic = new sns.Topic(this, 'SystemMonitorTopic');

    // topic.addSubscription(new subs.SqsSubscription(queue));
     //////////////////  Layers ///////////////////////
    const layer1 = new lambda.LayerVersion(this, 'ip_analysis_layer', {
      compatibleRuntimes: [
        lambda.Runtime.PYTHON_3_8,
        lambda.Runtime.PYTHON_3_9,
      ],
      code: lambda.Code.fromAsset(path.join(__dirname,'../src/layers','ip_analysis.zip')),
      description: 'multiplies a number by 2',
    });
    // const Function_vbs_system_monitor = new lambda.Function(this, 'Function_vbs_system_monitor', {
    //   runtime: lambda.Runtime.PYTHON_3_8,
    //   handler: 'app.lambda_handler',
    //   code: lambda.Code.fromAsset(path.join(__dirname,'../src/systemMonitor')),
    //   functionName:'Function_vbs_system_monitor',
    //   timeout: Duration.seconds(600),
    //   layers:[layer1]
    // });
     
    const Function_vbs_system_monitor = new lambda.DockerImageFunction(this, 'Function_vbs_system_monitor',{
      functionName: 'Function_vbs_system_monitor',
      code: lambda.DockerImageCode.fromImageAsset(path.join(__dirname, '../src/systemMonitor'), {
      cmd: [ "app.lambda_handler" ],
      }),
      timeout: Duration.seconds(900),
  });
    const Policy_vbs_system_monitor = new iam.PolicyStatement();
    Policy_vbs_system_monitor.addResources("*");
    Policy_vbs_system_monitor.addActions("*");
    Function_vbs_system_monitor.addToRolePolicy(Policy_vbs_system_monitor);

    const eventRule_vbs_system_monitor=new events.Rule(this, "monitorRule", {
    
      // schedule:events.Schedule.rate(cdk.Duration.minutes(3))
      // schedule:events.Schedule.rate(cdk.Duration.days(1))
      // schedule:events.Schedule.cron(hour=10,12,* ,* ,? *)
      schedule:events.Schedule.expression("cron(0 2 * * ? *)")
    });

    eventRule_vbs_system_monitor.addTarget(
      new targets.LambdaFunction(Function_vbs_system_monitor, {
        event: events.RuleTargetInput.fromObject({ message: "Hello Lambda" }),
      })
    );

    targets.addLambdaPermission(eventRule_vbs_system_monitor, Function_vbs_system_monitor);

      
  }
}
