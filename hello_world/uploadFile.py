import json
import logging
import boto3
from botocore.exceptions import ClientError

# import requests

bucket_name = "communet-bucket"

def lambda_handler(event, context):
    
    object_name : str | None = json.loads(event['body'])['file_name']
    
    print(object_name)
    
    if(object_name is None):
        return {
            "statusCode" : 404,
            "body" : "No file name found"
        }
    
    
    s3 = boto3.client("s3")
    
    global bucket_name
    
    url : str | None = create_presigned_url(
        s3,
        bucket_name=bucket_name,
        object_name=object_name)

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": url,
        }),
    }



def create_presigned_url(s3_client,bucket_name, object_name, expiration=3600):

    s3_client = boto3.client('s3')
    try:
        response = s3_client.generate_presigned_url('put_object',
                                                    Params={'Bucket': bucket_name,
                                                            'Key': object_name},
                                                    ExpiresIn=expiration)
    except ClientError as e:
        logging.error(e)
        return None

    return response