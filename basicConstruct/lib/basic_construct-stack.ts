import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as sqs from 'aws-cdk-lib/aws-sqs';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as resourcegroups from 'aws-cdk-lib/aws-resourcegroups';
import * as path from 'path';

export class BasicConstructStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // The code that defines your stack goes here

 
    // 監聽 CloudTrail 在 IAM 新建 user 時觸發



    // example resource
    // const queue = new sqs.Queue(this, 'BasicConstructQueue', {
    //   visibilityTimeout: cdk.Duration.seconds(300)
    // });

    // const cfnGroup = new resourcegroups.CfnGroup(this, 'MyCfnGroup', {
    //   name: 'name20221126',
    
    //   // the properties below are optional
      
    //   description: 'description',
   
      
    //   tags: [{
    //     key: '20221126',
    //     value: 'value',
    //   }],
    // });

    // const tag = new cdk.Tag('key-20221126', 'value', /* all optional props */ {
    //   applyToLaunchedInstances: true,
    //   excludeResourceTypes: ['excludeResourceTypes'],
    //   includeResourceTypes: ['includeResourceTypes'],
    //   priority: 123,
    // });


  }
}
