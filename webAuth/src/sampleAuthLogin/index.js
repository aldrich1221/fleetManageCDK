console.log('Loading function');

// dependencies
var AWS = require('aws-sdk');
var config = require('./config.json');
// var cryptoUtils = require('./lib/cryptoUtils');


// Get reference to AWS clients
var dynamodb = new AWS.DynamoDB();
var cognitoidentity = new AWS.CognitoIdentity();

function getUser(userid, fn) {
	dynamodb.getItem({
		TableName: config.DDB_TABLE,
		Key: {
			userid: {
				S: userid
			}
		}
	}, function(err, data) {
		if (err) return fn(err);
		else {
			if ('Item' in data) {
				// var hash = data.Item.passwordHash.S;
				// var salt = data.Item.passwordSalt.S;
				// var verified = data.Item.verified.BOOL;
				var password=data.Item.userpassword.S;
				fn(null, password);
			} else {
				fn(null, null); // User not found
			}
		}
	});
}

// function getToken(userid, fn) {
// 	var param = {
// 		IdentityPoolId: config.IDENTITY_POOL_ID,
// 		Logins: {} // To have provider name in a variable
// 	};
// 	param.Logins[config.DEVELOPER_PROVIDER_NAME] = userid;
// 	cognitoidentity.getOpenIdTokenForDeveloperIdentity(param,
// 		function(err, data) {
// 			if (err) return fn(err); // an error occurred
// 			else fn(null, data.IdentityId, data.Token); // successful response
// 		});
// }
function getToken(userid, fn) {
	dynamodb.getItem({
		TableName: config.DDB_TABLE,
		Key: {
			userid: {
				S: "Enterprise_User_Service"
			}
		}
	}, function(err, data) {
		if (err) return fn(err);
		else {

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

			sts.assumeRole(roleToAssume, function(err, data) {
				if (err) return fn(err);
				else{
					roleCreds = {accessKeyId: data.Credentials.AccessKeyId,
								 secretAccessKey: data.Credentials.SecretAccessKey,
								 sessionToken: data.Credentials.SessionToken};

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
					fn(null, roleCreds.IdentityId,roleCreds.secretAccessKey, roleCreds.Token,keypair_id)
				}
			});
		

		}
	});

}

exports.handler = (event, context, callback) => {
	console.log("=========event--------")
	console.log(event)
	var userid = event.userid;
	var clearPassword = event.password;

	getUser(userid, function(err, password) {
		if (err) {
			callback('Error in getUser: ' + err);
		} else {
			if (password== null) {
				// User not found
				console.log('User not found: ' + userid);
				callback(null, { login: false	});
			} else {
				
				console.log('clearPassword' + clearPassword + ' password: ' + password);
				if (clearPassword == password) {
					// Login ok
					console.log('User logged in: ' + userid);
					getToken(userid, function(err, identityId,secretAccessKey, token,apitoken) {
						if (err) {
							callback('Error in getToken: ' + err);
						} else {
							callback(null, {
								login: true,
								identityId: identityId,
								secretAccessKey:secretAccessKey,
								token: token,
								apitoken:apitoken
							});
						}
					});
				} else {
					// Login failed
					console.log('User login failed: ' + userid);
					callback(null, { login: false });
				}
				
			}
		}
	});
}
