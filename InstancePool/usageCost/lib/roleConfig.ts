

    const dataPipelineDefaultRole = new iam.Role(this, 'dataPipelineDefaultRole', {
      assumedBy: new iam.CompositePrincipal(
        new iam.ServicePrincipal('datapipeline.amazonaws.com'),
        new iam.ServicePrincipal('elasticmapreduce.amazonaws.com'),
      ),
    })

    const dataPipelineDefaultResourceRole = new iam.Role(this, 'dataPipelineDefaultResourceRole', {
      assumedBy: new iam.ServicePrincipal('ec2.amazonaws.com'),
    })

    const Policy_vbs_datapipeline = new iam.PolicyStatement();
    Policy_vbs_datapipeline.effect=iam.Effect.ALLOW
    Policy_vbs_datapipeline.addResources("*");
    Policy_vbs_datapipeline.addActions("*");


    const Policy_vbs_datapipeline2 = new iam.PolicyStatement();
    Policy_vbs_datapipeline2.effect=iam.Effect.ALLOW
    Policy_vbs_datapipeline2 .addResources("*");
    Policy_vbs_datapipeline2 .addActions("elasticmapreduce:TerminateJobFlows");
    Policy_vbs_datapipeline2 .addActions("elasticmapreduce:ListSteps");
    Policy_vbs_datapipeline2 .addActions("elasticmapreduce:ListClusters");
    Policy_vbs_datapipeline2 .addActions("elasticmapreduce:RunJobFlow");
    Policy_vbs_datapipeline2 .addActions("elasticmapreduce:DescribeCluster");
    Policy_vbs_datapipeline2 .addActions("elasticmapreduce:AddTags");
    Policy_vbs_datapipeline2 .addActions("elasticmapreduce:RemoveTags");
    Policy_vbs_datapipeline2 .addActions("elasticmapreduce:ListInstanceGroups");
    Policy_vbs_datapipeline2 .addActions("elasticmapreduce:ModifyInstanceGroups");
    Policy_vbs_datapipeline2 .addActions("elasticmapreduce:GetCluster");
    Policy_vbs_datapipeline2 .addActions("elasticmapreduce:DescribeStep");
    Policy_vbs_datapipeline2 .addActions("elasticmapreduce:AddJobFlowSteps");
    Policy_vbs_datapipeline2 .addActions("elasticmapreduce:ListInstances");



    const Policy_vbs_datapipeline3 = new iam.PolicyStatement( )
    Policy_vbs_datapipeline3.effect=iam.Effect.ALLOW
    Policy_vbs_datapipeline3.addActions("iam:*");
    Policy_vbs_datapipeline3.addActions("iam:ListInstanceProfiles");
    Policy_vbs_datapipeline3 .addResources(dataPipelineDefaultRole.roleArn);
    Policy_vbs_datapipeline3 .addResources(dataPipelineDefaultResourceRole.roleArn);
    Policy_vbs_datapipeline3 .addResources("*");

    const Policy_vbs_datapipeline4 = new iam.PolicyStatement( )
    Policy_vbs_datapipeline4.effect=iam.Effect.ALLOW
    Policy_vbs_datapipeline4.addActions("ec2:*");
    Policy_vbs_datapipeline4 .addResources("*");
    
    const Policy_vbs_datapipeline5 = new iam.PolicyStatement( )
    Policy_vbs_datapipeline5.effect=iam.Effect.ALLOW
    Policy_vbs_datapipeline5.addActions("s3:*");
    Policy_vbs_datapipeline5 .addResources(s3Bucket.bucketArn);

    const Policy_vbs_datapipeline6 = new iam.PolicyStatement( )
    Policy_vbs_datapipeline6.effect=iam.Effect.ALLOW
    Policy_vbs_datapipeline6.addActions("dynamodb:*");
    Policy_vbs_datapipeline6.addResources(table2.tableArn);
        
    dataPipelineDefaultRole.addToPolicy(Policy_vbs_datapipeline)
    dataPipelineDefaultRole.addToPolicy(Policy_vbs_datapipeline2)
    dataPipelineDefaultRole.addToPolicy(Policy_vbs_datapipeline3)
    dataPipelineDefaultRole.addToPolicy(Policy_vbs_datapipeline4)
    dataPipelineDefaultRole.addToPolicy(Policy_vbs_datapipeline5)
    dataPipelineDefaultRole.addToPolicy(Policy_vbs_datapipeline6)

    
    // dataPipelineDefaultRole.addManagedPolicy(iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSDataPipeline_FullAccess'))
    // dataPipelineDefaultRole.addManagedPolicy(iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSDataPipelineRole'))


    const Policy_vbs_datapipelineresource = new iam.PolicyStatement( )
    Policy_vbs_datapipelineresource.effect=iam.Effect.ALLOW
    Policy_vbs_datapipelineresource.addActions("cloudwatch:*");
    Policy_vbs_datapipelineresource.addActions("datapipeline:*");
    Policy_vbs_datapipelineresource.addActions("dynamodb:*");
    Policy_vbs_datapipelineresource.addActions("ec2:Describe*");
    Policy_vbs_datapipelineresource.addActions("elasticmapreduce:*");
    Policy_vbs_datapipelineresource.addActions("s3:*");
    Policy_vbs_datapipelineresource.addActions("iam:*");
    Policy_vbs_datapipelineresource.addActions("sdb:*");
    Policy_vbs_datapipelineresource.addActions("sns:*");
    Policy_vbs_datapipelineresource.addActions("sqs:*");
    // Policy_vbs_datapipelineresource.addResources("*");
    Policy_vbs_datapipelineresource.addResources(dataPipelineDefaultRole.roleArn);
    Policy_vbs_datapipelineresource.addResources(dataPipelineDefaultResourceRole.roleArn);

    dataPipelineDefaultResourceRole.addToPolicy(Policy_vbs_datapipeline)
    dataPipelineDefaultResourceRole.addToPolicy(Policy_vbs_datapipelineresource)

    const cfnInstanceProfile = new iam.CfnInstanceProfile(this, 'MyCfnInstanceProfile', {
      roles: [dataPipelineDefaultResourceRole.roleName],
      instanceProfileName: dataPipelineDefaultResourceRole.roleName,
    });


    dataPipelineDefaultResourceRole.addManagedPolicy(
      iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AmazonEC2RoleforDataPipelineRole'),
    )






