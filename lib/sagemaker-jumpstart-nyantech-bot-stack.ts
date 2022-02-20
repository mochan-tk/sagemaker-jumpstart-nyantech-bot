import { Stack, StackProps, Duration } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as lambda from "aws-cdk-lib/aws-lambda";
import * as apigateway from 'aws-cdk-lib/aws-apigateway';
import { Role, ServicePrincipal, ManagedPolicy } from 'aws-cdk-lib/aws-iam';
// import * as sqs from 'aws-cdk-lib/aws-sqs';

export class SagemakerJumpstartNyantechBotStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    // IAM Role for Lambda with SSM policy.
    const lambdaRole = new Role(this, 'SageMakerJumpstartNyantechBotLambdaRole', {
      roleName: 'SageMakerJumpstartNyantechBotLambdaRole',
      assumedBy: new ServicePrincipal('lambda.amazonaws.com'),
      managedPolicies: [
        //ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSLambdaBasicExecutionRole'),
        ManagedPolicy.fromAwsManagedPolicyName('AdministratorAccess'),
      ]
    });    

    const bot = new lambda.DockerImageFunction(this, 'sagemaker-jumpstart-nyantech-bot', {
      code: lambda.DockerImageCode.fromImageAsset('./lambda/bot'),
      role: lambdaRole,
      timeout: Duration.seconds(30),
    });

    const api = new apigateway.RestApi(this, 'sagemaker-jumpstart-nyantech-api');
    api.root.addMethod('POST', new apigateway.LambdaIntegration(bot));
  }
}
