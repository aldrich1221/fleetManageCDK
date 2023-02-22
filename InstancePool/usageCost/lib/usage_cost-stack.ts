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
// import * as d2s from 'data-pipeline-d2s-cdk';

export class UsageCostStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);


    

    // The code below shows an example of how to instantiate this type.
// The values are placeholders you should change.
  
 

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

    const s3Bucket = new s3.Bucket(this, 's3-bucket', {
      // bucketName: 'my-bucket',
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      autoDeleteObjects: true,
      versioned: false,
      publicReadAccess: false,
      encryption: s3.BucketEncryption.S3_MANAGED,
      // cors: [
      //   {
      //     allowedMethods: [
      //       s3.HttpMethods.GET,
      //       s3.HttpMethods.POST,
      //       s3.HttpMethods.PUT,
      //     ],
      //     allowedOrigins: ['http://localhost:3000'],
      //     allowedHeaders: ['*'],
      //   },
      // ],
      // lifecycleRules: [
      //   {
      //     abortIncompleteMultipartUploadAfter: cdk.Duration.days(90),
      //     expiration: cdk.Duration.days(365),
      //     transitions: [
      //       {
      //         storageClass: s3.StorageClass.INFREQUENT_ACCESS,
      //         transitionAfter: cdk.Duration.days(30),
      //       },
      //     ],
      //   },
      // ],
    });

    // 👇 grant access to bucket
    s3Bucket.grantRead(new iam.AccountRootPrincipal());

    const pipelineid="VBS_datapipeline"
    const bucketName=s3Bucket.bucketName
    const tableName="VBS_User_UsageAndCost"
    const throughputRatio=0.8
    const resizeClusterBeforeRunning = true
    const period={
      value: 15,
      format: 'Minute'
    }
    const emrTerminateAfter={
      value: 1,
      format: 'Minute'
    }
    const runOccurrences = 1
    const scheduleType ="cron"
    const failureAndRerunMode ="CASCADE"


    const dataPipelineDefaultRole = new iam.Role(this, 'dataPipelineDefaultRole', {
      assumedBy: new iam.CompositePrincipal(
        new iam.ServicePrincipal('datapipeline.amazonaws.com'),
        new iam.ServicePrincipal('elasticmapreduce.amazonaws.com'),
      ),
    })
    const dataPipelineDefaultResourceRole = new iam.Role(this, 'dataPipelineDefaultResourceRole', {
      assumedBy: new iam.ServicePrincipal('ec2.amazonaws.com'),
    })

    const Policy_vbs_datapipeline = new iam.PolicyStatement();
    Policy_vbs_datapipeline .addResources("*");
    Policy_vbs_datapipeline .addActions("*");


    const Policy_vbs_datapipeline2 = new iam.PolicyStatement();
    Policy_vbs_datapipeline2 .addResources("*");
    Policy_vbs_datapipeline2 .addActions("elasticmapreduce:*");

    const Policy_vbs_datapipeline3 = new iam.PolicyStatement( )
    Policy_vbs_datapipeline3.addActions("iam:*");
    Policy_vbs_datapipeline3 .addResources(dataPipelineDefaultRole.roleArn);
    Policy_vbs_datapipeline3 .addResources(dataPipelineDefaultResourceRole.roleArn);
    Policy_vbs_datapipeline3 .addResources("*");
    const Policy_vbs_datapipeline4 = new iam.PolicyStatement( )
    Policy_vbs_datapipeline4.addActions("ec2:*");
    Policy_vbs_datapipeline4 .addResources("*");
    
    const Policy_vbs_datapipeline5 = new iam.PolicyStatement( )
    Policy_vbs_datapipeline5.addActions("s3:*");
    Policy_vbs_datapipeline5 .addResources(s3Bucket.bucketArn);

    const Policy_vbs_datapipeline6 = new iam.PolicyStatement( )
    Policy_vbs_datapipeline6.addActions("dynamodb:*");
    Policy_vbs_datapipeline6 .addResources(table2.tableArn);
        
    dataPipelineDefaultRole.addToPolicy(Policy_vbs_datapipeline)
    dataPipelineDefaultRole.addToPolicy(Policy_vbs_datapipeline2)
    dataPipelineDefaultRole.addToPolicy(Policy_vbs_datapipeline3)
    dataPipelineDefaultRole.addToPolicy(Policy_vbs_datapipeline4)
    dataPipelineDefaultRole.addToPolicy(Policy_vbs_datapipeline5)
    dataPipelineDefaultRole.addToPolicy(Policy_vbs_datapipeline6)



    // Function_vbs_message_consumer.addToRolePolicy(Policy_vbs_message_consumer);
    
    // dataPipelineDefaultRole.addManagedPolicy(ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSDataPipelineRole'))
    // dataPipelineDefaultRole.addManagedPolicy(iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSDataPipelineRole'))

    const Policy_vbs_datapipelineresource = new iam.PolicyStatement( )
    Policy_vbs_datapipelineresource.addActions("cloudwatch:*");
    Policy_vbs_datapipelineresource.addActions("datapipeline:*");
    Policy_vbs_datapipelineresource.addActions("dynamodb:*");
    Policy_vbs_datapipelineresource.addActions("ec2:Describe*");
    Policy_vbs_datapipelineresource.addActions("elasticmapreduce:*");
    Policy_vbs_datapipelineresource.addActions("s3:*");
    Policy_vbs_datapipelineresource.addActions("iam:*");
    Policy_vbs_datapipelineresource.addActions("sdb:*");
    Policy_vbs_datapipelineresource.addActions("sns:*");
    Policy_vbs_datapipelineresource.addActions("sqs:*");
    Policy_vbs_datapipelineresource.addResources("*");
    Policy_vbs_datapipelineresource.addResources(dataPipelineDefaultRole.roleArn);
    Policy_vbs_datapipelineresource.addResources(dataPipelineDefaultResourceRole.roleArn);

  

    dataPipelineDefaultResourceRole.addToPolicy(Policy_vbs_datapipeline)
    dataPipelineDefaultResourceRole.addToPolicy(Policy_vbs_datapipelineresource)

    const cfnInstanceProfile = new iam.CfnInstanceProfile(this, 'MyCfnInstanceProfile', {
      roles: [dataPipelineDefaultResourceRole.roleName],
      instanceProfileName: dataPipelineDefaultResourceRole.roleName,
    });


    dataPipelineDefaultResourceRole.addManagedPolicy(
      iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AmazonEC2RoleforDataPipelineRole'),
    )



    // new iam.CfnInstanceProfile(this, 'dataPipelineDefaultResourceRoleInstanceProfile', {
    //   roles: [dataPipelineDefaultResourceRole.roleName],
    //   instanceProfileName: dataPipelineDefaultResourceRole.roleName,
    // })


    new datapipeline.CfnPipeline(this, pipelineid, {
      name: id,
      parameterObjects: [],
      pipelineObjects: [
        {
          id: 'S3BackupLocation',
          name: 'Copy data to this S3 location',
          fields: [
            {
              key: 'type',
              stringValue: 'S3DataNode',
            },
            {
              key: 'dataFormat',
              refValue: 'DDBExportFormat',
            },
            {
              key: 'directoryPath',
              stringValue: `s3://${bucketName}/#{format(@scheduledStartTime, 'YYYY-MM-dd-HH-mm-ss')}`,
            },
          ],
        },
        {
          id: 'DDBSourceTable',
          name: 'DDBSourceTable',
          fields: [
            {
              key: 'tableName',
              stringValue: tableName,
            },
            {
              key: 'type',
              stringValue: 'DynamoDBDataNode',
            },
            {
              key: 'dataFormat',
              refValue: 'DDBExportFormat',
            },
            {
              key: 'readThroughputPercent',
              stringValue: `${throughputRatio}`,
            },
          ],
        },
        {
          id: 'DDBExportFormat',
          name: 'DDBExportFormat',
          fields: [
            {
              key: 'type',
              stringValue: 'DynamoDBExportDataFormat',
            },
          ],
        },
        {
          id: 'TableBackupActivity',
          name: 'TableBackupActivity',
          fields: [
            {
              key: 'resizeClusterBeforeRunning',
              stringValue: `${resizeClusterBeforeRunning}`,
            },
            {
              key: 'type',
              stringValue: 'EmrActivity',
            },
            {
              key: 'input',
              refValue: 'DDBSourceTable',
            },
            {
              key: 'runsOn',
              refValue: 'EmrClusterForBackup',
            },
            {
              key: 'output',
              refValue: 'S3BackupLocation',
            },
          ],
        },
        {
          id: 'DefaultSchedule',
          name: 'RunPerMonth',
          fields: [
            {
              key: 'occurrences',
              stringValue: `${runOccurrences}`,
            },
            {
              key: 'startAt',
              stringValue: 'FIRST_ACTIVATION_DATE_TIME',
            },
            {
              key: 'type',
              stringValue: 'Schedule',
            },
            {
              key: 'period',
              stringValue: `${period.value} ${period.format}`,
            },
          ],
        },
        {
          id: 'Default',
          name: 'Default',
          fields: [
            {
              key: 'type',
              stringValue: 'Default',
            },
            {
              key: 'scheduleType',
              stringValue: scheduleType,
            },
            {
              key: 'failureAndRerunMode',
              stringValue: failureAndRerunMode,
            },
            {
              key: 'role',
              stringValue: dataPipelineDefaultRole.roleName,
            },
            {
              key: 'resourceRole',
              stringValue: dataPipelineDefaultResourceRole.roleName,
            },
            {
              key: 'schedule',
              refValue: 'DefaultSchedule',
            },
          ],
        },
        {
          id: 'EmrClusterForBackup',
          name: 'EmrClusterForBackup',
          fields: [
            {
              key: 'terminateAfter',
              stringValue: `${emrTerminateAfter.value} ${emrTerminateAfter.format}`,
            },
            {
              key: 'type',
              stringValue: 'EmrCluster',
            },
          ],
        },
      ],
    })
  }
}
