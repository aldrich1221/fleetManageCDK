console.log('Loading function');

// dependencies
var AWS = require('aws-sdk');
var config = require('./config.json');
// var cryptoUtils = require('./lib/cryptoUtils');
import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import { DEFAULT_REGION } from "../../../../libs/utils/util-aws-sdk.js";
// Create an Amazon DynamoDB service client object.
export const ddbClient = new DynamoDBClient({ region: DEFAULT_REGION });
import { GetCommand } from "@aws-sdk/lib-dynamodb";
import { ddbDocClient } from "../libs/ddbDocClient.js";

// Set the parameters.


export const getItem = async (params) => {
  try {
    const data = await ddbDocClient.send(new GetCommand(params));
    console.log("Success :", data.Item);
  } catch (err) {
    console.log("Error", err);
  }
  return data
};
const AWS = require("aws-sdk");

const dynamo = new AWS.DynamoDB.DocumentClient();
// Get reference to AWS clients
var dynamodb = new AWS.DynamoDB();
var cognitoidentity = new AWS.CognitoIdentity();

function getUser(userid) {
	console.log("========get user----------")
	const params = {
		TableName: "VBS_Enterprise_Info",
		Key: {
		  primaryKey: userid,
		  
		},
	  };
	const data=getItem(params);
	// var data=dynamodb.getItem({
	// 	TableName: "VBS_Enterprise_Info",
	// 	Key: {
	// 		userid: {
	// 			S: userid
	// 		}
	// 	}
	// })
	console.log("========get user dtat----------")
	console.log(data)

	if ('Item' in data) {
		// var hash = data.Item.passwordHash.S;
		// var salt = data.Item.passwordSalt.S;
		// var verified = data.Item.verified.BOOL;
		var password=data.Item.userpassword.S;
		return password
	} else {
		return null
	}
	}


function getToken(userid) {
	console.log("========get token--------")
	
	const params = {
		TableName: "VBS_Enterprise_Info",
		Key: {
		  primaryKey: "Enterprise_User_Service",
		  
		},
	  };
	
	
	
	var data=getItem(params);
	// var data=dynamodb.getItem({
	// 	TableName: config.DDB_TABLE,
	// 	Key: {
	// 		userid: {
	// 			S: "Enterprise_User_Service"
	// 		}
	// 	}
	// })

	console.log("========get db--------")
	console.log(data)
	

	var iam_role_arn=data.Item.iam_role_arn.S;
	var keypair_id=data.Item.keypair_id.S;
	var keypair_secret=data.Item.keypair_secret.S

	AWS.config.update({region: 'us-east-1'});
	
	var roleToAssume = {RoleArn: iam_role_arn,
						RoleSessionName: userid+'session1',
						DurationSeconds: 900,};

	var roleCreds;
	
	// Create the STS service object    
	var sts = new AWS.STS({apiVersion: '2011-06-15',accessKeyId:keypair_id,secretAccessKey:keypair_secret});
	console.log("========sts========")
	console.log(sts)

	var data2=sts.assumeRole(roleToAssume)
	
	
	roleCreds = {accessKeyId: data2.Credentials.AccessKeyId,
					secretAccessKey: data2.Credentials.SecretAccessKey,
					sessionToken: data2.Credentials.SessionToken,
					apiKey:keypair_id};

	var stsParams = {credentials: roleCreds };
			// Create STS service object
			// var sts = new AWS.STS(stsParams);
				
			// sts.getCallerIdentity({}, function(err, data) {
			// 	if (err) {
			// 		console.log(err, err.stack);
			// 	}
			// 	else {
			// 		console.log(data.Arn);
			// 	}
			// });    
	console.log("assueRole success")
	console.log(stsParams)

	return roleCreds
}
			
		

	



exports.handler = (event, context, callback) => {
	console.log("=========event--------")
	console.log(event)

	var userid = event.headers.userid;
	var clearPassword = event.headers.password;

	const response=getUser(userid)
	if (response==null){
		return ({'status':'fail','data':'Error in getUser'})
	}else{

		if (clearPassword == password) {
			// Login ok
			console.log('User logged in: ' + userid);
			var roleCreds=getToken(userid)
			roleCreds['login']=true
			return ({'status':'success','data':roleCreds})
			
		} else {
			// Login failed
			console.log('User login failed: ' + userid);
			// callback(null, { login: false });
			return ({'status':'fail','data':{ login: false	}})
		}

	}
	
	

	console.log("=======final--------")
	console.log(response)
	return response;
}
