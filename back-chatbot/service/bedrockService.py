import re
import json
import asyncio
import boto3
import aioboto3
import traceback 
from botocore.exceptions import ClientError

from prompt.prompt_b import systemPrompt as model_b_sysPrompt
from prompt.prompt_c import systemPrompt as model_c_sysPrompt
from prompt.prompt_d import systemPrompt as model_d_sysPrompt
from prompt.prompt_e import systemPrompt as model_e_sysPrompt
from prompt.prompt_f import systemPrompt as model_f_sysPrompt

from service.serverlessService import invoke_lambda_function

from service.websocketService import send_to_websocket


def get_bedrock_response(model_result):

    try:
        # 비동기 작업을 위한 이벤트 루프 생성 및 실행
        loop = asyncio.get_event_loop()
        
        # 이벤트 루프가 닫혀있으면 새로 생성
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # 병렬 처리 실행 (model_result 전달)

        results = loop.run_until_complete(process_parallel_requests_with_dependencies(model_result))
        lambda_response = invoke_lambda_function(results)
        
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

# FastAPI용 비동기 버전 추가
async def get_bedrock_response_async(model_result):
    try:
        # 비동기 함수 직접 호출 (이미 이벤트 루프에서 실행 중)
        results = await process_parallel_requests_with_dependencies(model_result)
        lambda_response = invoke_lambda_function(results)
        
        return lambda_response
    
    except Exception as e:
        print(f"오류 발생: {str(e)}")
        # 오류 발생 시 기본값 반환
        return [f"오류가 발생했습니다: {str(e)}", None]

def invoke_userReponse(max_token, system_prompt, user_message):
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
        "system": system_prompt,
        "messages": [
            {
                "role": "user", 
                "content": user_message
            }
        ]
    }
    
    # 일반 모델 호출 (스트리밍 아님)
    response = bedrock_runtime.invoke_model(
        modelId='anthropic.claude-3-5-sonnet-20240620-v1:0',
        contentType="application/json",
        accept="application/json",
        body=json.dumps(payload)
    )
    
    raw_body = response['body'].read()
    decoded_body = raw_body.decode("utf-8")
    data = json.loads(decoded_body)
    text_data = data["content"][0]["text"]

    send_to_websocket(text_data)

    return text_data

async def invoke_bedrock_model(max_token, system_prompt, message):

    print(f"bedrock 함수호출: {message[:20]}...")    

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
    #A모델 max_tokens : 2500 / USER_RESPONSE, MODEL_DATA
    #B모델 max_tokens : 4000 / 
    #C모델 max_tokens : 4000 / files [filename, content]
    #D모델 max_tokens : 2000 / visual_tree
    #E모델 max_tokens : 4000 / project_name, 
    #                          source_files[file_path,content], 
    #                          build_configuration[file_path,content]
    #                          build_configuration[file_path,content]
    #F모델 max_tokens : 4000 / USER_RESPONSE[file_name, content]
    #                          PROVISIONING_SCRIPTS[file_path,content]
    #                          BUILD_SCRIPTS[file_path,content]
    results = {}
    
    try:
        requires_cloud = parse_requires_cloud(model_result)
        print(f"parse_requires_cloud 결과: {requires_cloud}")

    except Exception as e:
        print(f"parse_requires_cloud 오류: {str(e)}")
        print(f"오류 발생 위치: {traceback.format_exc()}")
    
    # B 모델 시작
    #task_b = asyncio.create_task(invoke_bedrock_model(4000, model_b_sysPrompt, model_result))
    #results['modelB'] = await task_b

    task_c = None
    if requires_cloud:
        print("aws 환경 포함")
        task_c = asyncio.create_task(
            invoke_bedrock_model(4000, model_c_sysPrompt, model_result)
        )
    else:
        print("aws 환경 미포함")
    
    # D 모델 시작
    task_d = asyncio.create_task(
        invoke_bedrock_model(2000, model_d_sysPrompt, model_result)
    )
    
    # D의 결과 기다리기
    model_d_result = await task_d
    results['modelD'] = model_d_result
    send_to_websocket(results['modelD'])
    
    print("D 완료, E와 F 시작")
    
    # D의 결과를 가지고 E와 F 시작
    task_e = asyncio.create_task(
        invoke_bedrock_model(4000, model_e_sysPrompt, model_d_result)
    )
    task_f = asyncio.create_task(
        invoke_bedrock_model(3500, model_f_sysPrompt, model_d_result)
    )
    
    
    # C 모델은 requires_cloud가 true일 경우에만 실행되었으므로, 결과도 조건부로 저장
    if task_c:
        results['modelC'] = await task_c
        send_to_websocket(results['modelC'])

    else:
        results['modelC'] = "no data"
    
    results['modelE'] = await task_e
    results['modelF'] = await task_f
    send_to_websocket(results['modelE'])
    send_to_websocket(results['modelF'])
    
    print("모든 모델 호출 완료")

    return results

def parse_requires_cloud(text):
    pattern = r'requires_cloud:\s*(true|false)'
    
    try:
        match = re.search(pattern, text, re.IGNORECASE)
        print(f"정규식 매치 결과: {match}")
        
        # 매치가 있으면 해당 값을 boolean으로 변환하여 반환
        if match and match.group(1):
            result = match.group(1).lower() == 'true'
            print(f"매치된 값: {match.group(1)}, 변환 결과: {result}")
            return result
    except Exception as e:
        print(f"정규식 처리 중 오류: {str(e)}")
        print(f"오류 발생 위치: {traceback.format_exc()}")
    
    # 매치가 없으면 기본값으로 False 반환
    print("매치 없음, 기본값 False 반환")
    return False