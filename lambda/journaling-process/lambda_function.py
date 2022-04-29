import json
import boto3
import os
import uuid
import time
from common.cibic_common import *
from datetime import datetime, timezone

snsClient = boto3.client('sns')
dynamoDbClient = boto3.client('dynamodb')
dynamoDbResource = boto3.resource('dynamodb')

snsTopicArn = os.environ['ENV_VAR_SNS_TOPIC_JOURNALING_DATA_READY']
journalingDataTableName = os.environ['ENV_VAR_DYNAMODB_JOURNALING_DATA_TABLE']

def lambda_handler(event, context):
    processedIds = [] # holds item keys to send to SNS after processing.
    journalingDataTable = dynamoDbResource.Table(journalingDataTableName) # table client for processed journals.
    if 'Records' in event:
        # There are record updates from the jounral requests table.
        for rec in event['Records']:
            # Interate through each record... 

            # Set some scoped vars for the parsing operation.
            request = None
            journal_data = None

            # get time of processing 
            time_now = datetime.now().astimezone(tz=timezone.utc).isoformat() # time for system resources
            time_for_sort = int(time.time()) # time for sorting

            try: 
                # Tries parsing data out of records.
                if rec['eventName'] == 'INSERT':
                    # New data was inserted into the request table.

                    # Grab the new image of the record that was inserted.
                    item = rec['dynamodb']['NewImage']
                    
                    # Parse AWS structured data into a python formatted dict.
                    request = unmarshallAwsDataItem(item)

                    # Print some info to cloudwatch for debugging
                    print('processing journaling request {} ({}), data {}'
                            .format(request['requestId'], request['timestamp'], request['body']))
                    
                    # The request body is stored as a string. Let's unmarshal it into a dict.
                    journal_data = json.loads( request['body'] )
            except:
                # There was an issue getting data from the record.
                print('issue parsing data from record.')
                err = reportError() 
                continue

            try:
                # Tries getting external data to join into journal entries
                # TODO: Get user/ride information
                pass
            except:
                # There was an issue getting data about user or ride.
                print('issue getting external data.')
                err = reportError() 
                pass

            # detirmine entry type.
            entryType = 'unclassified'
            if journal_data['type'] in ['reflection', 'live']:
                entryType = journal_data['type']
            
            try:
                # Tries updating user profiles.
                # Upserts the 'profile' of a user which contains highlevel information about their journaled rides.            
                journalingDataTable.update_item(
                    Key={
                        'userId': journal_data['userId'],
                        'sortKey': 'profile'
                    },
                    UpdateExpression = "SET #last_update = :last_update ADD #num_reflections :num_reflections, #num_live :num_live",
                    ExpressionAttributeNames={
                        '#last_update': 'lastUpdate',
                        '#num_reflections': 'numReflections',
                        '#num_live': 'numLive'
                    },
                    ExpressionAttributeValues={
                        ':last_update': time_now,
                        ':num_reflections': 1 if entryType == 'reflection' else 0,
                        ':num_live': 1 if entryType == 'live' else 0
                    }
                )
            except:
                print('issue updating users journal profile.')
                err = reportError() 
                pass
            try: 
                # Create a new item for processed journals.
                # Structures data for table to allow "adjacency list" type queries. 
                if entryType == "reflection":
                    journalingDataTable.put_item(Item = {
                        'userId': journal_data['userId'],
                        'sortKey':  entryType +'-'+ str(time_for_sort),
                        'created': time_now,
                        'request': request,
                        'dbVersion': 0,
                        'role': journal_data['role'],
                        'media': journal_data['image'],
                        'type': journal_data['type'],
                        'answers': journal_data['answers'],
                        'journal': journal_data['journal']
                    })
                if entryType == "live":
                    journalingDataTable.put_item(Item = {
                        'userId': journal_data['userId'],
                        'sortKey':  entryType +'-'+ str(time_for_sort),
                        'created': journal_data['time'],
                        'request': request,
                        'dbVersion': 0,
                        'role': journal_data['role'],
                        'type': journal_data['type'],
                        'data': journal_data['data'],
                    })

            except:
                print('issue adding users journal entry.')
                err = reportError() 
                continue

            # store processed id here for SNS notify later
            processedIds.append(    
                {   
                    "userId": journal_data['userId'],
                    "sortKey": entryType +'-'+ str(time_for_sort)
                }
            )

        try:
            # Tries to publish a notification to the proper channels.
            snsClient.publish(
                    TopicArn=snsTopicArn,
                    Message=json.dumps(processedIds),
                    Subject='journaling-raw',
                )
        except:
            err = reportError()
            return lambdaReply(420, str(err)) 
    else:
        return malformedMessageReply()

    return lambdaReply(200, processedIds)
