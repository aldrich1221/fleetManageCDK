import { Duration, Stack, StackProps } from 'aws-cdk-lib';
import * as sns from 'aws-cdk-lib/aws-sns';
import * as subs from 'aws-cdk-lib/aws-sns-subscriptions';
import * as sqs from 'aws-cdk-lib/aws-sqs';
import { Construct } from 'constructs';
import * as datapipeline from 'aws-cdk-lib/aws-datapipeline';
import * as cdk from 'aws-cdk-lib';
import * as iam from 'aws-cdk-lib/aws-iam';
import {SqsEventSource} from 'aws-cdk-lib/aws-lambda-event-sources';

import * as apigateway from 'aws-cdk-lib/aws-apigateway'
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as s3 from 'aws-cdk-lib/aws-s3';
// import * as d2s from 'data-pipeline-d2s-cdk';

export class UsageCostStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    // const queue = new sqs.Queue(this, 'UsageCostQueue', {
    //   visibilityTimeout: Duration.seconds(300)
    // });

    // const topic = new sns.Topic(this, 'UsageCostTopic');

    // topic.addSubscription(new subs.SqsSubscription(queue));

    // const { tableName } = new dynamodb.Table(this, 'Table', {
    //   partitionKey: { name: 'id', type: dynamodb.AttributeType.STRING }
    // })
    // const { bucketName } = new s3.Bucket(this, 'MyBucket')
     
    // const {d2sObject}=new d2s.DataPipelineD2SCdk(this, 'DataPipeline', {
    //   tableName,
    //   bucketName,
    //   throughputRatio: 0.2,
    //   period: {
    //     value: 1,
    //     format: d2s.TimeFormat.Day,
    //   },
    //   emrTerminateAfter: {
    //     value: 1,
    //     format: d2s.TimeFormat.Minute
    //   },
    // })

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
    // s3Bucket.grantRead(new iam.AccountRootPrincipal());

    const pipelineid="VBS_datapipeline"
    const bucketName=s3Bucket.bucketName
    const tableName="VBS_User_UsageAndCost"
    const throughputRatio=0.8
    const resizeClusterBeforeRunning = true
    const period={
      value: 6,
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

    // const Policy_vbs_datapipeline = new iam.PolicyStatement();
    // Policy_vbs_datapipeline .addResources("*");
    // Policy_vbs_datapipeline .addActions("*");
    // Function_vbs_message_consumer.addToRolePolicy(Policy_vbs_message_consumer);
    
    // dataPipelineDefaultRole.addManagedPolicy(ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSDataPipelineRole'))
    // dataPipelineDefaultRole.addManagedPolicy(iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSDataPipelineRole'))


    const dataPipelineDefaultResourceRole = new iam.Role(this, 'dataPipelineDefaultResourceRole', {
      assumedBy: new iam.ServicePrincipal('ec2.amazonaws.com'),
    })
    // dataPipelineDefaultResourceRole.addManagedPolicy(
    //   iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AmazonEC2RoleforDataPipelineRole'),
    // )



    new iam.CfnInstanceProfile(this, 'dataPipelineDefaultResourceRoleInstanceProfile', {
      roles: [dataPipelineDefaultResourceRole.roleName],
      instanceProfileName: dataPipelineDefaultResourceRole.roleName,
    })
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
              stringValue: 'HiveCopyActivity',
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
          name: 'RunOnce',
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
