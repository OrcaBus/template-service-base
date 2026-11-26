import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { DeploymentStackPipeline } from '@orcabus/platform-cdk-constructs/deployment-stack-pipeline';
import { getStackProps } from '../stage/config';
import { HelloWorldStack } from '../stage/deployment-stack';

export class StatelessStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const pipeline = new DeploymentStackPipeline(this, 'DeploymentPipeline', {
      githubBranch: 'main',
      githubRepo: 'template-service-base',
      stack: HelloWorldStack,
      stackName: 'HelloWorldStack',
      stackConfig: {
        beta: getStackProps('BETA'),
        gamma: getStackProps('GAMMA'),
        prod: getStackProps('PROD'),
      },
      pipelineName: 'OrcaBus-StatelessHelloWorld',
      cdkSynthCmd: ['pnpm install --frozen-lockfile --ignore-scripts', 'pnpm cdk-stateless synth'],
      unitAppTestConfig: {
        command: ['cd app && make install && make check && make test'],
      },
    });

    // The pipeline's roles, buckets, keys and projects come from the platform construct
    for (const id of [
      'AwsSolutions-IAM4',
      'AwsSolutions-IAM5',
      'AwsSolutions-S1',
      'AwsSolutions-KMS5',
      'AwsSolutions-CB3',
    ]) {
      cdk.Validations.of(pipeline).acknowledge({ id, reason: 'Allow CDK Pipeline' });
    }
  }
}
