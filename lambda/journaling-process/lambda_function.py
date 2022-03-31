import json
import boto3
import os
import uuid
from common.cibic_common import *
from datetime import datetime

snsClient = boto3.client('sns')
dynamoDbClient = boto3.client('dynamodb')
dynamoDbResource = boto3.resource('dynamodb')

snsTopicArn = os.environ['ENV_VAR_SNS_TOPIC_JOURNALING_DATA_READY']
journalingDataTableName = os.environ['ENV_VAR_DYNAMODB_JOURNALING_DATA_TABLE']

def lambda_handler(event, context):
    processedIds = []
    journalingDataTable = dynamoDbResource.Table(journalingDataTableName)

    try:
        print ('event data ' + str(event))

        # DynamoDB table stream provides event that has multiple records
        # while in practice, there should be just one record when someone
        # adds data to the table, in theory there could be a batch of records
        # so we need to account for that
        if 'Records' in event:
            for rec in event['Records']:
                if rec['eventName'] == 'INSERT': # when new data inserted
                    item = dynamoDbClient.get_item(
                        TableName = CibicResources.DynamoDB.ModeratedJournalingRequests,
                        Key=rec['dynamodb']['Keys'])
                    request = unmarshallAwsDataItem(item['Item'])

                    journal_data = json.loads( request['body'] )

                    print('processing journaling request {} ({}), data {}'
                            .format(request['requestId'], request['timestamp'], request['body']))
                    
                    # Create base record 
                    ProcessedRecord = {
                        'requestId': request['requestId'],
                        'body': request['body'],
                    }

                    # Parse request body
                    requestData = json.loads(request['body'])
                    
                    if 'userid' in requestData:
                        # Request can be correlated to user
                        ProcessedRecord.update(requestData)
                        ProcessedRecord['GSI1PK'] = requestData['userid']



                    # store data in DynamoDB table
                    time_now = int(time.time())
                    journalingDataTable.put_item(Item = {
                        'userId': journal_data['userId'],
                        'sortKey': "journal-" + str(time_now),
                        'created': time_now,
                        'request': request,
                        'dbVersion': 0,
                        'role': journal_data['role'],
                        'media': journal_data['image'],
                        'type': journal_data['type']
                    })
                    # store processed id here for SNS notify later
                    processedIds.append(    
                        {   
                            "userId": journal_data['userId'],
                            "sortKey": "journal-"+str(time_now)
                        }
                    )

            snsClient.publish(
                    TopicArn=snsTopicArn,
                    Message=json.dumps(processedIds),
                    Subject='journaling-raw',
                )
        else:
            return malformedMessageReply()
    except:
        err = reportError()
        print('caught exception:', sys.exc_info()[0])
        return lambdaReply(420, str(err))

    return lambdaReply(200, processedIds)
