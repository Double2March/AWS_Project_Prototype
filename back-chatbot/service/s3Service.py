import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key

# S3 버킷 초기화
s3_client = boto3.client('s3', region_name='ap-northeast-2')
BUCKET_NAME = "your-s3-bucket-name"  # 실제 S3 버킷 이름으로 변경하세요

def upload_to_s3(file_name, content):
    """S3에 파일 업로드"""
    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=file_name,
        Body=content.encode('utf-8')
    )

def generate_presigned_url(file_name):
    """S3 파일에 대한 presigned URL 생성"""
    return s3_client.generate_presigned_url(
        'get_object',
        Params={
            'Bucket': BUCKET_NAME,
            'Key': file_name
        },
        ExpiresIn=3600  # URL 유효 기간: 1시간
    )
