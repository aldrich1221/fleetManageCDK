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
import { aws_inspector as inspector } from 'aws-cdk-lib';

export class InspectorStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // The code that defines your stack goes here

    // example resource
    // const queue = new sqs.Queue(this, 'InspectorQueue', {
    //   visibilityTimeout: cdk.Duration.seconds(300)
    // });

    // const cfnAssessmentTemplate = new inspector.CfnAssessmentTemplate(this, 'MyCfnAssessmentTemplate', {
    //   assessmentTargetArn: 'assessmentTargetArn',
    //   durationInSeconds: 123,
    //   rulesPackageArns: ['rulesPackageArns'],
    
    //   // the properties below are optional
    //   assessmentTemplateName: 'assessmentTemplateName',
    //   userAttributesForFindings: [{
    //     key: 'key',
    //     value: 'value',
    //   }],
    // });

  //   const Function_vbs_localtest = new lambda.DockerImageFunction(this, 'Function_vbs_localtest',{
  //     functionName: 'Function_vbs_localtest',
  //     code: lambda.DockerImageCode.fromImageAsset(path.join(__dirname, '../../src/test'), {
  //     cmd: [ "app.lambda_handler" ],
    
     
  //     }),
  //     timeout: Duration.seconds(900),
  // });



      // const Function_vbs_localtest=new lambda.Function(this, 'Function_vbs_inspectorTest', {
      //   functionName: 'Function_vbs_inspectorTest',
      //   runtime: lambda.Runtime.PYTHON_3_7,
      //   handler: 'app.lambda_handler',
       
      //   code: lambda.Code.fromAsset(path.join(__dirname, '../../src/inspectorTest')),
      // });

      
  }
}

