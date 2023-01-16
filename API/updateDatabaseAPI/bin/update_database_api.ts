#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { UpdateDatabaseApiStack } from '../lib/update_database_api-stack';

const app = new cdk.App();
new UpdateDatabaseApiStack(app, 'UpdateDatabaseApiStack');
