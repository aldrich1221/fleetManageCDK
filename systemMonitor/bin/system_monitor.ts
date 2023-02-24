#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { SystemMonitorStack } from '../lib/system_monitor-stack';

const app = new cdk.App();
new SystemMonitorStack(app, 'SystemMonitorStack');
