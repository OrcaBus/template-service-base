#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { StatelessStack } from '../infrastructure/toolchain/stateless-stack';
import { StatefulStack } from '../infrastructure/toolchain/stateful-stack';
import { TOOLCHAIN_ENVIRONMENT } from '@orcabus/platform-cdk-constructs/deployment-stack-pipeline';
import { HelloWorldStack } from '../infrastructure/stage/deployment-stack';

const app = new cdk.App();

const deployMode = app.node.tryGetContext('deployMode');
if (!deployMode) {
  throw new Error("deployMode is required in context (e.g. '-c deployMode=stateless')");
}

if (deployMode === 'stateless') {
  new StatelessStack(app, 'OrcaBusStatelessHelloWorldStack', {
    env: TOOLCHAIN_ENVIRONMENT,
  });
} else if (deployMode === 'direct') {
  new HelloWorldStack(app, 'HelloWorldStack', {
    env: {
      account: process.env.CDK_DEFAULT_ACCOUNT,
      region: process.env.CDK_DEFAULT_REGION ?? 'ap-southeast-2',
    },
    mainBusName: process.env.EVENT_BUS_NAME ?? 'OrcaBusMain',
    stage: 'dev',
  });
} else if (deployMode === 'stateful') {
  new StatefulStack(
    app,
    /* TODO: Replace with string. Example: */ 'OrcaBusStateful{ServiceName}Stack',
    {
      env: TOOLCHAIN_ENVIRONMENT,
    }
  );
} else {
  throw new Error("Invalid 'deployMode` set in the context");
}
