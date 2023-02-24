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
import * as ec2 from 'aws-cdk-lib/aws-ec2';

import * as codepipeline from 'aws-cdk-lib/aws-codepipeline';
import * as codebuild from 'aws-cdk-lib/aws-codebuild';
import * as codecommit from 'aws-cdk-lib/aws-codecommit';
import * as codepipeline_actions from 'aws-cdk-lib/aws-codepipeline-actions';

import * as ecr from 'aws-cdk-lib/aws-ecr';

import * as sns_subscriptions from 'aws-cdk-lib/aws-sns-subscriptions';
import * as targets from 'aws-cdk-lib/aws-events-targets';
import { MakeDirectoryOptions } from "fs";


export interface PipelineStackProps extends StackProps {
  readonly ecr_repo: string;
  readonly codecommit_repo: string;
  readonly codecommit_branch: string;
  readonly codebuild_project: string;
  readonly codepipeline_name: string;
  readonly notifications_email: string;
}
export class CicdStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);


    ////////////////////////////////////////////////////////  Jenkins server  ///////////////////////////
  //   const cicdRole = new iam.Role(this, 'cicdRole', {
  //     assumedBy: new iam.CompositePrincipal(
  //       new iam.ServicePrincipal("ec2.amazonaws.com"),
  //       new iam.ServicePrincipal("spotfleet.amazonaws.com"),
  //       new iam.ServicePrincipal("s3.amazonaws.com"),
  //       new iam.ServicePrincipal("dynamodb.amazonaws.com"),
  //     ),
  //   })
  

  //   const Policy_vbs_cicd = new iam.PolicyStatement();
  //   Policy_vbs_cicd.addResources("*");
  //   Policy_vbs_cicd.addActions("*");
  //   cicdRole.addToPolicy(Policy_vbs_cicd)

  //   const cfnInstanceProfile = new iam.CfnInstanceProfile(this, 'MyCfnInstanceProfile', {
  //     roles: [cicdRole.roleName],
  //     instanceProfileName: cicdRole.roleName+"_InstanceProfile",
  //   });


  // const spotOptionsRequestProperty: ec2.CfnEC2Fleet.SpotOptionsRequestProperty = {
  //     allocationStrategy: 'lowest-price',
  //     instancePoolsToUseCount: 2,
  //     maintenanceStrategies: {
  //       capacityRebalance: {
  //         replacementStrategy: 'launch-before-terminate',
  //         terminationDelay: 10,
  //       },
  //     },
  //     maxTotalPrice: '0.0021',
  //     minTargetCapacity: 1,
  //     singleAvailabilityZone: false,
  //     singleInstanceType: false,
  //   };
    
  //   const cfnEC2Fleet = new ec2.CfnEC2Fleet(this, 'MyCfnEC2Fleet', {
  //     launchTemplateConfigs: [{
  //       launchTemplateSpecification: {
  //         version: 'version',
  //       },
       
  //     }],
  //     targetCapacitySpecification: {
  //       totalTargetCapacity: 1,
  //     },
  //     replaceUnhealthyInstances: false,
  //     spotOptions:spotOptionsRequestProperty,
     
  //     terminateInstancesWithExpiration: false,
     
  //   });



    ///////////////////////////  code pipeline ///////////////////////////

    var ecrRepository_name="vbsInstancePoolECR"
    var codecommitRepository_name="vbsInstancePoolCodeCommit"
    var codebuildProject_name="vbsInstancePoolCodeBuild"
    var codepipeline_name='vbsInstancePoolCodePipeline'
    var notifications_email='aldrich_chen@htc.com'


    // const user = new iam.User(this, 'User');

   
    const ecrRepository = new ecr.Repository(this, 'Repo', {
      imageScanOnPush: true,
     
    });
  
    

    const codecommitRepository = new codecommit.Repository(this, 'Repository', {
      repositoryName: codecommitRepository_name,
      description: 'Some description.', // optional property
    });

    
    const codebuildProject = new codebuild.PipelineProject(this, "Build", {
      projectName: codebuildProject_name,
      environment: {
        computeType: codebuild.ComputeType.SMALL,
        buildImage: codebuild.LinuxBuildImage.AMAZON_LINUX_2_3,
        privileged: true,
        environmentVariables: {
          AWS_ACCOUNT_ID: {
            type: codebuild.BuildEnvironmentVariableType.PLAINTEXT,
            value: '867217160264'
          },
          AWS_DEFAULT_REGION: {
            type: codebuild.BuildEnvironmentVariableType.PLAINTEXT,
            value: 'us-east-1'
          }
        }
      }
    });

    // codebuild policy of codecommit pull source code.
    const codeBuildPolicyOfcodeCommit = new iam.PolicyStatement();
    codeBuildPolicyOfcodeCommit.addResources(codecommitRepository.repositoryArn)
    codeBuildPolicyOfcodeCommit.addActions(
      "codecommit:ListBranches",
      "codecommit:ListRepositories",
      "codecommit:BatchGetRepositories",
      "codecommit:GitPull"
    );
    codebuildProject.addToRolePolicy(
      codeBuildPolicyOfcodeCommit,
    );
    // codebuild policy of ecr build
    const codeBuildPolicyEcr = new iam.PolicyStatement();
    codeBuildPolicyEcr.addAllResources()
    codeBuildPolicyEcr.addActions(
      "ecr:GetAuthorizationToken",
      "ecr:InitiateLayerUpload",
      "ecr:UploadLayerPart",
      "ecr:CompleteLayerUpload",
      "ecr:BatchCheckLayerAvailability",
      "ecr:PutImage"
    )
    codebuildProject.addToRolePolicy(codeBuildPolicyEcr);


    // /**
    //  * CodePipeline: 
    //  * 1. create codebuild project
    //  * 2. create policy of ECR and Codecommit
    // **/

    // // trigger of `CodeCommitTrigger.POLL`
    const sourceOutput = new codepipeline.Artifact();
    const sourceAction = new codepipeline_actions.CodeCommitSourceAction({
      actionName: "Source-CodeCommit",
      branch: 'main',
      trigger: codepipeline_actions.CodeCommitTrigger.POLL,
      repository: codecommitRepository,
      output: sourceOutput
    });

    // // when codecommit input then action of codebuild
    const buildOutput = new codepipeline.Artifact();
    const buildAction1 = new codepipeline_actions.CodeBuildAction({
      actionName: "Build",
      input: sourceOutput,
      outputs: [
        buildOutput
      ],
      project: codebuildProject
    });

    const testOutput = new codepipeline.Artifact();
    const buildAction2 = new codepipeline_actions.CodeBuildAction({
      actionName: "Test",
      input: buildOutput,
      outputs: [
        testOutput
      ],
      project: codebuildProject
    });


    // // create pipeline, and then add both codecommit and codebuild  
    const pipeline = new codepipeline.Pipeline(this, "Pipeline", {
      pipelineName: codepipeline_name
    });
    pipeline.addStage({
      stageName: "Source",
      actions: [sourceAction]
    });
    pipeline.addStage({
      stageName: "Build",
      actions: [buildAction1]
    });

    pipeline.addStage({
      stageName: "Test",
      actions: [buildAction2]
    });
    // /**
    //  * SNS: Monitor pipeline state change then notifiy
    // **/
    if ( notifications_email ) {
      const pipelineSnsTopic = new sns.Topic(this, 'DemoPipelineStageChange');
      pipelineSnsTopic.addSubscription(new sns_subscriptions.EmailSubscription(notifications_email))
      pipeline.onStateChange("PipelineStateChange", {
        target: new targets.SnsTopic(pipelineSnsTopic), 
        description: 'Listen for codepipeline change events',
        eventPattern: {
          detail: {
            state: [ 'FAILED', 'SUCCEEDED', 'STOPPED' ]
          }
        }
      });
    }


    // // /**
    // //  * Output: 
    // //  * - CodeCommit clone path of HTTP and SSH
    // //  * - ECR Repository URI
    // // **/
    // new CfnOutput(this, 'CodeCommitCloneUrlHttp', {
    //   description: 'CodeCommit Repo CloneUrl HTTP',
    //   value: codecommitRepository.repositoryCloneUrlHttp
    // });
    // new CfnOutput(this, 'CodeCommitCloneUrlHttp', {
    //     description: 'CodeCommit Repo CloneUrl HTTP',
    //     value: codecommitRepository.repositoryCloneUrlHttp
    //   });

    // new CfnOutput(this, 'CodeCommitCloneUrlSsh', {
    //   description: 'CodeCommit Repo CloneUrl SSH',
    //   value: codecommitRepository.repositoryCloneUrlSsh
    // });

    // new CfnOutput(this, 'EcrRepositoryUri', {
    //   description: 'ECR Repository URI',
    //   value: ecrRepository.repositoryUri
    // });

  }
}
