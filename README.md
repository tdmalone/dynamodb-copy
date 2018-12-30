# dynamodb-copy

A simple Python 3.7 Lambda function that copies DynamoDB records from one table to another, in real-time.

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

3. From the DynamoDB console on your source table, select the _Triggers_ tab, and click _Create trigger_, following the prompts
4. Add a row to your source table and see how it goes!

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
