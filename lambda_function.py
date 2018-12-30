"""
From a DynamoDB stream, replicates records to another table, optionally adding a 'ttl' attribute.

@see https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Streams.html
@see https://docs.aws.amazon.com/lambda/latest/dg/with-ddb.html
@see https://github.com/techgaun/dynamodb-copy-table/blob/master/dynamodb-copy-table.py
@author Tim Malone <tim@timmalone.id.au>
"""

import logging

from os import getenv
from time import time
from boto3 import client

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Required variables.
destination_table = getenv('DESTINATION_TABLE_NAME')
destination_region = getenv('DESTINATION_TABLE_REGION')

# Optional variables - set *both* if you want to add a TTL attribute to the replicated records.
ttl_attribute = getenv('DESTINATION_TABLE_TTL_ATTRIBUTE')
ttl_seconds = getenv('TTL_SECONDS_FROM_NOW')

dynamodb = client('dynamodb', region_name=destination_region)

def lambda_handler(event, context):

  new_ttl = round(float(ttl_seconds) + time(), 0)

  for item in event['Records']:
    logger.debug(item['dynamodb'])

    if 'NewImage' not in item['dynamodb']:
      continue

    new_item = item['dynamodb']['NewImage']

    if ttl_attribute and ttl_seconds:
      new_item[ttl_attribute] = {'N': str(new_ttl)}

    dynamodb.put_item(TableName=destination_table, Item=new_item)

    logger.debug(new_item)
    logger.info('Imported a record.')

  logger.info('Done.')
  return 'Done.'
