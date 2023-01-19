import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * from '@aws-cdk/aws-stepfunctions-tasks';

// import * as sqs from 'aws-cdk-lib/aws-sqs';

export class BasicDbStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // The code that defines your stack goes here

    // example resource
    // const queue = new sqs.Queue(this, 'BasicDbQueue', {
    //   visibilityTimeout: cdk.Duration.seconds(300)
    // });
  }
}
