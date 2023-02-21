import { Duration, Stack, StackProps } from 'aws-cdk-lib';
import * as sns from 'aws-cdk-lib/aws-sns';
import * as subs from 'aws-cdk-lib/aws-sns-subscriptions';
import * as sqs from 'aws-cdk-lib/aws-sqs';
import { Construct } from 'constructs';
import * as datapipeline from 'aws-cdk-lib/aws-datapipeline';
import * as cdk from 'aws-cdk-lib';
import * as iam from 'aws-cdk-lib/aws-iam';
import {SqsEventSource} from 'aws-cdk-lib/aws-lambda-event-sources';
// import { aws_iam as iam2 } from 'aws-cdk-lib';

import * as apigateway from 'aws-cdk-lib/aws-apigateway'
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as s3 from 'aws-cdk-lib/aws-s3';

export class CicdStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);



    const cicdRole = new iam.Role(this, 'cicdRole', {
      assumedBy: new iam.CompositePrincipal(
        new iam.ServicePrincipal("ec2.amazonaws.com"),
        new iam.ServicePrincipal("spotfleet.amazonaws.com"),
        new iam.ServicePrincipal("s3.amazonaws.com"),
        new iam.ServicePrincipal("dynamodb.amazonaws.com"),
      ),
    })
  

    const Policy_vbs_cicd = new iam.PolicyStatement();
    Policy_vbs_cicd.addResources("*");
    Policy_vbs_cicd.addActions("*");
    cicdRole.addToPolicy(Policy_vbs_cicd)

  }
}
