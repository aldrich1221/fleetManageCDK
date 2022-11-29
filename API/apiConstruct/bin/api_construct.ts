#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { ApiConstructStack } from '../lib/api_construct-stack';

const app = new cdk.App();
new ApiConstructStack(app, 'ApiConstructStack');
