import json
import boto3
from boto3.dynamodb.conditions import Key, Attr
import os
import time
from common.cibic_common import *
from datetime import datetime, timezone, timedelta

snsClient = boto3.client('sns')
dynamoDbClient = boto3.client('dynamodb')
dynamoDbResource = boto3.resource('dynamodb')

snsTopicArn = os.environ['ENV_VAR_SNS_TOPIC_JOURNALING_DATA_READY']
journalingDataTableName = os.environ['ENV_VAR_DYNAMODB_JOURNALING_DATA_TABLE']

def lambda_handler(event, context):
    processedIds = [] # holds item keys to send to SNS after processing.
    journalingDataTable = dynamoDbResource.Table(journalingDataTableName)  # table client for processed journals.
    if 'Records' in event:
        # There are record updates from the jounral requests table.
        for rec in event['Records']:
            # Interate through each record... 

            # Set some scoped vars for the parsing operation.
            request = None
            journal_data = None

            one_day = timedelta(days=1) # cut off horizon for ride query 
            
            time_now = datetime.now() 
            time_now_formatted = time_now.astimezone(tz=timezone.utc).isoformat() # time for system resources
            
            time_a_day_ago = time_now - one_day
            time_a_day_ago_formatted = time_a_day_ago.astimezone(tz=timezone.utc).isoformat() # time for system resources
            
            time_for_sort = int(time.time()) # time for sorting

            # Check if record is a dynamoDB event
            if "dynamodb" in rec:
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

                # detirmine entry type.
                entryType = 'unclassified'
                if journal_data['type'] in ['reflection', 'live']:
                    entryType = journal_data['type']

                
                # Tries updating user profile. Profiles contain highlevel data about rides, flow, journal entries. 
                try:
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
                            ':last_update': time_now_formatted,
                            ':num_reflections': 1 if entryType == 'reflection' else 0,
                            ':num_live': 1 if entryType == 'live' else 0
                        }
                    )
                except:
                    print('issue updating users journal profile.')
                    err = reportError() 
                    pass
                
                # Tries to put the journal entry in the table. 
                try: 
                    # Create a new item for processed journals.
                    # Structures data for table to allow "adjacency list" type queries. 
                    if entryType == "reflection":
                        journalingDataTable.put_item(Item = {
                            'userId': journal_data['userId'],
                            'sortKey':  entryType +'-'+ str(time_for_sort),
                            'created': time_now_formatted,
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
                
                # if entry type is 'reflection' add it to a list to send via SNS to continue processing for censor and PII.
                if entryType == "reflection":
                    # store processed id here for SNS notify later
                    processedIds.append(    
                        {   
                            "userId": journal_data['userId'],
                            "sortKey": entryType +'-'+ str(time_for_sort)
                        }
                    )
        
        # if there are journals that need processing for censor ro PII - send the ids via SNS
        if len(processedIds) > 0:
            # There are ids that need more actions applied.
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
