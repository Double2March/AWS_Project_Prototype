import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key

lambda_client = boto3.client('lambda', region_name='ap-northeast-2')

#람다함수 동기 호출코드
def invoke_lambda(function_name, payload):
    
    response = lambda_client.invoke(
        FunctionName=function_name,
        InvocationType='RequestResponse',
        Payload=json.dumps(payload)
    )
    
    return json.loads(response['Payload'].read().decode('utf-8'))

#람다함수 비동기 호출코드
async def invoke_lambda_async(function_name, payload):    
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None, 
        lambda: invoke_lambda(function_name, payload)
    )


def invoke_lambda_function(results):
    """
    Lambda 함수를 호출하고 응답을 받는 함수
    """
    # AWS Lambda 클라이언트 초기화
    lambda_client = boto3.client('lambda', region_name='ap-northeast-2')
    
    # Lambda 함수 호출
    response = lambda_client.invoke(
        FunctionName='your-lambda-function-name',
        InvocationType='RequestResponse',
        Payload=json.dumps(results)
    )
    
    # Lambda 응답 처리
    response_payload = json.loads(response['Payload'].read())
    return response_payload  # [user_response, presignedUrls] 형식의 응답 기대