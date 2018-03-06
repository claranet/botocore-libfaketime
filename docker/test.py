import boto3
import botocore_libfaketime.patch

kms = boto3.client('kms')
s3 = boto3.client('s3')

for key in kms.list_keys()['Keys'][:3]:
    print key['KeyArn']

for bucket in s3.list_buckets()['Buckets'][:3]:
    print 's3://' + bucket['Name']
