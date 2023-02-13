#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { UsageCostStack } from '../lib/usage_cost-stack';

const app = new cdk.App();
new UsageCostStack(app, 'UsageCostStack');
