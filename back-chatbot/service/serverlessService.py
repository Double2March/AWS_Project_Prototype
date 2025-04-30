import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key

lambda_client = boto3.client('lambda', region_name='ap-northeast-2')

def invoke_lambda(function_name, payload):
    """람다 함수를 동기적으로 호출"""
    response = lambda_client.invoke(
        FunctionName=function_name,
        InvocationType='RequestResponse',
        Payload=json.dumps(payload)
    )
    
    return json.loads(response['Payload'].read().decode('utf-8'))

async def invoke_lambda_async(function_name, payload):
    """람다 함수를 비동기적으로 호출"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None, 
        lambda: invoke_lambda(function_name, payload)
    )

def process_lambda_result(result):
    """람다 함수 결과 처리"""
    # 여기서 람다 결과를 가공할 수 있습니다
    processed_result = f"처리 시간: {datetime.now().isoformat()}\n\n{result}"
    return processed_result
