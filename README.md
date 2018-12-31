# dynamodb-copy

A simple Python 3.7 Lambda function that copies DynamoDB records from one table to another, in real-time, using [DynamoDB Streams](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Streams.html).

Optionally supports adding a [TTL attribute](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/TTL.html) to the new items, to have them expire after a certain time (this is useful for use cases such as making 'recent-only' replica tables for quick scanning of new records, for instance).

## Usage

I'll add a Terraform or Serverless config of sorts at some stage, but in the meantime, set up looks a bit like this:

1. Create a new Lambda function, setting the runtime to Python 3.7, and copy in the [source code](lambda_function.py).
2. Ensure the function has an IAM role that gives it the following permissions at a minimum (replacing `ACCOUNT_ID`, `SOURCE_REGION_ID`, `SOURCE_TABLE_NAME`, `DESTINATION_REGION_ID` and `DESTINATION_TABLE_NAME` with the appropriate values):
  
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "dynamodb:ListStreams",
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetShardIterator",
        "dynamodb:DescribeStream",
        "dynamodb:GetRecords"
      ],
      "Resource": "arn:aws:dynamodb:SOURCE_REGION_ID:ACCOUNT_ID:table/SOURCE_TABLE_NAME/stream/*"
    },
    {
      "Effect": "Allow",
      "Action": "dynamodb:PutItem",
      "Resource": "arn:aws:dynamodb:DESTINATION_REGION_ID:ACCOUNT_ID:table/DESTINATION_TABLE_NAME"
    }
  ]
}
```

3. Ensure the function has environment variables defining `DESTINATION_TABLE_NAME` and `DESTINATION_TABLE_REGION` (the latter is only required if the table is in a different region to where you're running the function from), and if you want to use the optional TTL feature, `DESTINATION_TABLE_TTL_ATTRIBUTE` and `TTL_SECONDS_FROM_NOW`.
4. If you're using the TTL options, ensure you also [have TTL enabled on your destination table](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/time-to-live-ttl-how-to.html).
5. From the DynamoDB console on your source table, select the _Triggers_ tab, and click _Create trigger_, following the prompts
6. Add a row to your source table and see how it goes!

There's also another optional feature - data enrichment for each copied row. This is handled by [`enrich.py`](enrich.py). The version in this repo has my own custom data enrichments; feel free to use it as a template to make your own. You can also just leave the file out and everything will work without it.

## Running Locally

To test the function locally, ensure you have relevant [AWS credentials available](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html), uncomment the `lambda_handler()` line at the end of [`lambda_function.py`](lambda_function.py), and then run something similar to the following:

    $ DESTINATION_TABLE_NAME=your-table-name python lambda_function.py

## Feedback, improvements, suggestions...

...are all welcome. [Log an issue](https://github.com/tdmalone/dynamodb-copy/issues/new) or send a PR.

## TODO

* Add IaC configuration, either via Terraform or Serverless (or maybe CloudFormation)
* Add linting, tests and CI
* Add auto-deployment to CI

## License

[MIT](LICENSE).

## See also

* [ec2-instance-stop-start](https://github.com/tdmalone/ec2-instance-stop-start)
