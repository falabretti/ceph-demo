import boto3
from werkzeug.utils import secure_filename

s3 = boto3.client(
    's3',
    aws_access_key_id='NDQB93BF3UQZ156T5XE0',
    aws_secret_access_key='BDBlLNG3fel38ppwD9Owz41BMcsBtutWN7fkZqjf',
    endpoint_url='http://192.168.0.12'
)

def parse_date(date):
    try:
        return date.strftime("%m/%m/%Y %H:%M:%S")
    except Exception:
        return date

def get_download_url(bucket, key):
    try:
        url = s3.generate_presigned_url('get_object', ExpiresIn = 86400, Params={'Bucket': bucket, 'Key': key})
        return url
    except Exception:
        return '#'

def parse_object(bucket, object):
    return {
        'key': object['Key'],
        'last_modified': parse_date(object['LastModified']),
        'size': object['Size'],
        'url': get_download_url(bucket, object['Key'])
    }

def parse_bucket(bucket):
    return {
        'name': bucket['Name'],
        'creation_date': parse_date(bucket['CreationDate'])
    }

def list_buckets():
    response = s3.list_buckets()
    buckets = [parse_bucket(bucket) for bucket in response.get('Buckets', [])]
    return buckets

def create_bucket(bucket):
    s3.create_bucket(Bucket=bucket)

def list_objects(bucket):
    create_bucket(bucket)
    response = s3.list_objects(Bucket=bucket)
    objects = [parse_object(bucket, obj) for obj in response.get('Contents', [])]
    return objects

def upload_object(file, bucket):
    s3.put_object(Bucket=bucket, Key=secure_filename(file.filename), Body=file)

def delete_object(bucket, key):
    s3.delete_object(Bucket=bucket, Key=key)
