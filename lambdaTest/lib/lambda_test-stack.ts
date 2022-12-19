import { Duration, Stack, StackProps } from 'aws-cdk-lib';
import * as sns from 'aws-cdk-lib/aws-sns';
import * as subs from 'aws-cdk-lib/aws-sns-subscriptions';
import * as sqs from 'aws-cdk-lib/aws-sqs';
import { Construct } from 'constructs';
import * as secretsmanager from 'aws-cdk-lib/aws-secretsmanager';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as iam from 'aws-cdk-lib/aws-iam'
import * as cloudfront from 'aws-cdk-lib/aws-cloudfront'
import * as cloudfrontorigins from 'aws-cdk-lib/aws-cloudfront-origins'
import * as apigateway from 'aws-cdk-lib/aws-apigateway'
import * as path from 'path';
import * as acm from 'aws-cdk-lib/aws-certificatemanager'
export class LambdaTestStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    const Function_vbs_lambda_test = new lambda.Function(this, 'FUNCTION_vbs_lambda_test', {
      runtime: lambda.Runtime.PYTHON_3_8,
      handler: 'vbs_test.lambda_handler',
      code: lambda.Code.fromAsset(path.join(__dirname, 'lambda-src')),
      functionName:'FUNCTION_vbs_lambda_test'
    });
    const API_vbs_test = new apigateway.LambdaRestApi(this, 'API_vbs_lambda_test', {
      handler: Function_vbs_lambda_test,
      restApiName:'API_vbs_lambda_test',
      proxy: false,
      integrationOptions: {
        allowTestInvoke: false,
          timeout: Duration.seconds(5),
        },
      defaultCorsPreflightOptions: { allowOrigins: apigateway.Cors.ALL_ORIGINS },
    });
    const Policy_vbs_lambda_test= new iam.PolicyStatement();
    Policy_vbs_lambda_test.addResources("*");
    Policy_vbs_lambda_test.addActions("*");
    Function_vbs_lambda_test.addToRolePolicy(Policy_vbs_lambda_test); 

    const API_vbs_test_items = API_vbs_test.root.addResource('v1');
    API_vbs_test_items.addMethod('GET',
    new apigateway.LambdaIntegration(Function_vbs_lambda_test, {proxy: true}));

   
  }
}
