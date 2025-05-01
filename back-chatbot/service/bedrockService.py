import json
import asyncio
import boto3
import aioboto3

from prompt.prompt_a import systemPrompt as model_a_sysPrompt
from prompt.prompt_b import systemPrompt as model_b_sysPrompt
from prompt.prompt_c import systemPrompt as model_c_sysPrompt
from prompt.prompt_d import systemPrompt as model_d_sysPrompt
from prompt.prompt_e import systemPrompt as model_e_sysPrompt
from prompt.prompt_f import systemPrompt as model_f_sysPrompt

from prompt.prompt_a import test_prompt as model_a_input
from prompt.prompt_b import test_prompt as model_b_input
from prompt.prompt_c import test_prompt as model_c_input
from prompt.prompt_d import test_prompt as model_d_input
from prompt.prompt_e import test_prompt as model_e_input
from prompt.prompt_f import test_prompt as model_f_input


async def invoke_bedrock_model(max_token,systemPrompt,message):
    print("함수호출")
    # Bedrock 클라이언트 초기화
    bedrock_runtime = boto3.client(
        service_name='bedrock-runtime',
        region_name='ap-northeast-2'  # 사용 중인 리전
    )
    
    # 페이로드 구성
    payload = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_token,
        "temperature": 0.2,
        "top_p": 0.2,
        "top_k": 50,
        "system": systemPrompt,
        "messages": [
            {
                "role": "user", 
                "content": message
            }
        ]
    }
    
    # 일반 모델 호출
    response = bedrock_runtime.invoke_model(
        modelId='anthropic.claude-3-5-sonnet-20240620-v1:0',
        contentType="application/json",
        accept="application/json",
        body=json.dumps(payload)
    )
    
    try:
        raw_body = response['body'].read()
        decoded_body = raw_body.decode("utf-8")
        data = json.loads(decoded_body)
        text_data = data["content"][0]["text"] 

    return text_data


def get_bedrock_response(model_result):
    """
    메인 함수: 병렬 처리를 수행하고 Lambda 응답을 반환
    """
    try:
        # 비동기 작업을 위한 이벤트 루프 생성 및 실행
        loop = asyncio.get_event_loop()
        
        # 이벤트 루프가 닫혀있으면 새로 생성
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # 병렬 처리 실행
        results = loop.run_until_complete(process_parallel_requests_with_dependencies(model_result))
        
        # Lambda 함수 호출 및 응답 처리
        lambda_response = invoke_lambda_function(results)
        
        # Lambda에서 받은 [user_response, presignedUrls] 반환
        return lambda_response
    
    except Exception as e:
        print(f"오류 발생: {str(e)}")
        # 오류 발생 시 기본값 반환
        return [f"오류가 발생했습니다: {str(e)}", None]
    
    finally:
        # 이벤트 루프 닫기 (필요한 경우)
        try:
            if loop and not loop.is_closed():
                loop.close()
        except:
            pass
            
async def invoke_bedrock_model(max_token, system_prompt, input_message):
    """
    Bedrock 모델을 비동기적으로 호출하는 함수
    """
    print(f"함수호출: {message[:20]}...")
    session = aioboto3.Session()
    async with session.client(
        service_name='bedrock-runtime',
        region_name='ap-northeast-2'
    ) as bedrock_runtime:
        # 페이로드 구성
        payload = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_token,
            "temperature": 0.2,
            "top_p": 0.2,
            "top_k": 50,
            "system": system_prompt,
            "messages": [
                {
                    "role": "user", 
                    "content": message
                }
            ]
        }
        
        # 비동기 모델 호출
        response = await bedrock_runtime.invoke_model(
            modelId='anthropic.claude-3-5-sonnet-20240620-v1:0',
            contentType="application/json",
            accept="application/json",
            body=json.dumps(payload)
        )
        
        raw_body = await response['body'].read()
        decoded_body = raw_body.decode("utf-8")
        data = json.loads(decoded_body)
        text_data = data["content"][0]["text"]
        
        return text_data

async def process_parallel_requests_with_dependencies(model_result):
    """
    의존성이 있는 병렬 처리를 수행하는 함수
    """
    # 결과를 저장할 딕셔너리
    results = {}
    results['modelA'] = model_result
    
    #A모델 max_tokens : 2500 / USER_RESPONSE, MODEL_DATA
        #B모델 max_tokens : 2500 / 
        #C모델 max_tokens : 4000 / files [filename, content]
        #D모델 max_tokens : 2000 / visual_tree
        #E모델 max_tokens : 4000 / project_name, 
        #                          source_files[file_path,content], 
        #                          build_configuration[file_path,content]
        #                          build_configuration[file_path,content]
        #F모델 max_tokens : 3500 / USER_RESPONSE[file_name, content]
        #                          PROVISIONING_SCRIPTS[file_path,content]
        #                          BUILD_SCRIPTS[file_path,content]

    #modelA = await invoke_bedrock_model(2500, model_a_sysPrompt, model_a_input) 
    #modelC = await invoke_bedrock_model(4000, model_c_sysPrompt, model_c_input) 
    #modelD = await invoke_bedrock_model(2000, model_d_sysPrompt, model_d_input)
    #modelE = await invoke_bedrock_model(4000, model_e_sysPrompt, model_e_input)
    #modelF = await invoke_bedrock_model(3500, model_f_sysPrompt, model_f_input)

    # B, C, D를 병렬로 시작
    #task_C = asyncio.create_task(invoke_bedrock_model(1000, "당신은 유용한 AI 비서입니다.", "B 모델 요청입니다: 파이썬의 장점에 대해 알려주세요."))

    requires_cloud = False
    try:
        if "MODEL_DATA" in model_result:
            requires_cloud = model_result["MODEL_DATA"].get("requires_cloud", False)
    except Exception as e:
        print(f"requires_cloud 추출 오류: {str(e)}")
        requires_cloud = False


    task_c = asyncio.create_task(
        invoke_bedrock_model(4000, model_c_sysPrompt, model_result)
    )
    task_d = asyncio.create_task(
        invoke_bedrock_model(2000, model_d_sysPrompt, model_result)
    )
    
    print(task_c)
    print(task_d)

    # D의 결과 기다리기
    model_d_result = await task_d
    results['modelD'] = await task_d  
    print("D 완료, E와 F 시작")
    
    # D의 결과를 가지고 E와 F 시작
    task_e = asyncio.create_task(
        invoke_bedrock_model(4000, model_e_sysPrompt, model_d_result)
    )
    task_f = asyncio.create_task(
        invoke_bedrock_model(3500, model_f_sysPrompt, model_d_result)
    )
    
    # 나머지 모든 결과 대기
    results['modelB'] = await task_b
    results['modelC'] = await task_c
    results['modelE'] = await task_e
    results['modelF'] = await task_f
    
    print("모든 모델 호출 완료")
    return results

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

# AWS Lambda 핸들러 함수(Lambda 함수를 구현할 경우) - 참고용
def lambda_handler(event, context):
    """
    Lambda 함수 핸들러 - 참고용
    이 함수는 [user_response, presignedUrls] 형식의 응답을 반환해야 합니다.
    """
    model_results = event  # event가 이미 모델 결과를 포함하는 딕셔너리
    
    # 여기서 결과 처리 로직 구현
    # ...
    
    user_response = "Lambda 처리 완료 메시지"
    presigned_urls = ["url1", "url2", "url3"]  # 실제 presigned URL 목록
    
    return [user_response, presigned_urls]