import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { DeploymentStackPipeline } from '@orcabus/platform-cdk-constructs/deployment-stack-pipeline';
import { DeployStack } from '../stage/deployment-stack';
import { getStackProps } from '../stage/config';

export class StatefulStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    new DeploymentStackPipeline(this, 'DeploymentStackPipeline', {
      githubBranch: 'main',
      githubRepo: 'orcabus/template-service-base',
      stackName: 'DeployStack',
      stack: DeployStack,
      stackConfig: {
        beta: getStackProps('BETA'),
        gamma: getStackProps('GAMMA'),
        prod: getStackProps('PROD'),
      },
      pipelineName: 'DeploymentPipeline',
      cdkSynthCmd: ['pnpm install --frozen-lockfile', 'pnpm cdk-stateless synth'],
    });
  }
}
