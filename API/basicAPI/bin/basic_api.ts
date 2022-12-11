#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { BasicApiStack } from '../lib/basic_api-stack';

const app = new cdk.App();
new BasicApiStack(app, 'BasicApiStack');
