#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { WebAuthStack } from '../lib/web_auth-stack';

const app = new cdk.App();
new WebAuthStack(app, 'WebAuthStack');
