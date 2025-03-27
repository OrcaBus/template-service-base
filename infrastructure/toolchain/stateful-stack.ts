import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { DeploymentStackPipeline } from 'test-platform-cdk-constructs/deployment-stack-pipeline';
import { DeployStack } from '../stage/deployment-stack';

export class StatefulStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    new DeploymentStackPipeline(this, 'DeploymentStackPipeline', {
      githubBranch: 'main',
      githubRepo: 'orcabus/template-service-base',
      stackName: 'DeployStack',
      stack: DeployStack,
      stackConfig: { beta: {}, gamma: {}, prod: {} },
      pipelineName: 'DeploymentPipeline',
      cdkSynthCmd: ['pnpm i'],
    });
  }
}
