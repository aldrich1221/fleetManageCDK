#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { ContentStatusStack } from '../lib/content_status-stack';

const app = new cdk.App();
new ContentStatusStack(app, 'ContentStatusStack');
