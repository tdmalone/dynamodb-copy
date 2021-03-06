"""
From a DynamoDB stream, replicates records to another table, optionally adding a 'ttl' attribute.

@see https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Streams.html
@see https://docs.aws.amazon.com/lambda/latest/dg/with-ddb.html
@see https://github.com/techgaun/dynamodb-copy-table/blob/master/dynamodb-copy-table.py
@author Tim Malone <tim@timmalone.id.au>
"""

import sys
import logging

from os import getenv
from time import time
from boto3 import client

# REQUIRED: The table name to copy records to.
destination_table = getenv('DESTINATION_TABLE_NAME')

# The AWS region of the destination table - if not the same as where you're running this function.
destination_region = getenv('DESTINATION_TABLE_REGION')

# Set *both* of these if you want to add a TTL attribute to the replicated records.
# @see https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/TTL.html
ttl_attribute = getenv('DESTINATION_TABLE_TTL_ATTRIBUTE')
ttl_seconds = getenv('TTL_SECONDS_FROM_NOW')

# @see https://docs.python.org/3/library/logging.html#logging-levels
LOGGING_LEVEL = getenv('LOGGING_LEVEL', 'INFO')

# Set up logging level, and stream stream to stdout if not running in Lambda.
# (We don't want to change the basicConfig if we ARE running in Lambda).
logger = logging.getLogger(__name__)
if getenv('AWS_EXECUTION_ENV') is None:
  logging.basicConfig(stream=sys.stdout, level=LOGGING_LEVEL)
else:
  logger.setLevel(LOGGING_LEVEL)

dynamodb = client('dynamodb', region_name=destination_region)

# Allow us to enrich the data if we have the optional module available (enrich.py).
try: from enrich import enrich
except: pass

def lambda_handler(event, context):

  if destination_table is None:
    raise ValueError('Please supply the destination table as the env var DESTINATION_TABLE_NAME')

  if 'Records' not in event or len(event['Records']) == 0:
    raise KeyError('No records are available to copy')

  for item in event['Records']:

    if 'dynamodb' not in item:
      logger.error('Record does not have DynamoDB data')
      continue

    logger.debug(item['dynamodb'])

    if 'NewImage' not in item['dynamodb']:
      logger.info('Record does not have a NewImage to process')
      continue

    new_item = item['dynamodb']['NewImage']

    if ttl_attribute and ttl_seconds:
      new_ttl = round(float(ttl_seconds) + time(), 0)
      new_item[ttl_attribute] = {'N': str(new_ttl)}

    if 'enrich' in globals():
      new_item = enrich(new_item)

    dynamodb.put_item(TableName=destination_table, Item=new_item)

    logger.debug(new_item)
    logger.info('Imported a record.')

  logger.info('Done.')
  return 'Done.'

# The following lambda_handler line is NOT needed to run this as a Lambda function, but you can
# uncomment it if you want to test the function locally. You'll need to replace 'id' with the name
# of your table's primary key, and then run something like:
#
#   $ DESTINATION_TABLE_NAME=your-table-name python lambda_function.py
#
#lambda_handler({'Records':[{'dynamodb':{'NewImage':{'id':{'S':'1'}}}}]}, {})
