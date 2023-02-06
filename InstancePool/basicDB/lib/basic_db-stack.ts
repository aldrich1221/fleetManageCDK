import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as sqs from 'aws-cdk-lib/aws-sqs';
// import * from '@aws-cdk/aws-stepfunctions-tasks';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
// import * as sqs from 'aws-cdk-lib/aws-sqs';

import { LambdaToSqsToLambda, LambdaToSqsToLambdaProps } from "@aws-solutions-constructs/aws-lambda-sqs-lambda";
import * as lambda from 'aws-cdk-lib/aws-lambda';

export class BasicDbStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // The code that defines your stack goes here


    /// instance pool table
    const table = new dynamodb.Table(this, 'Table', { 
      tableName:'VBS_Instance_Pool',
      partitionKey: { name: 'instanceId', type: dynamodb.AttributeType.STRING }, 
      billingMode: dynamodb.BillingMode.PROVISIONED, 
      readCapacity: 20,
      writeCapacity: 20,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      sortKey: {name: 'region', type: dynamodb.AttributeType.STRING},
      pointInTimeRecovery: true,
      tableClass: dynamodb.TableClass.STANDARD,


    });

    //  table.addLocalSecondaryIndex({
    //    indexName: 'activity_enterprise_Index',
    //    sortKey: {name: 'status', type: dynamodb.AttributeType.STRING},
    //    projectionType: dynamodb.ProjectionType.ALL
    // });

    table.addGlobalSecondaryIndex({
      indexName: 'gsi_zone_available_index',
      partitionKey: {name: 'zone', type: dynamodb.AttributeType.STRING},
      sortKey: {name: 'available', type: dynamodb.AttributeType.STRING},
      readCapacity: 1,
      writeCapacity: 1,
      projectionType: dynamodb.ProjectionType.ALL,
    });

    
    
    
    

  }
}
