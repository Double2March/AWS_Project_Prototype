import os
import re
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

async def invoke_bedrock_model(max_token, system_prompt, message):
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
    # 결과를 저장할 딕셔너리
    results = {}
    
    requires_cloud = extract_requires_cloud(model_result)
    print(requires_cloud)
    
    # B 모델 시작
    #task_b = asyncio.create_task(invoke_bedrock_model(1000, "당신은 유용한 AI 비서입니다.", f"B 모델 요청입니다: 다음 서비스 요약을 확장해주세요: {service_summary}"))
    
    task_c = None
    if requires_cloud:
        print("requires_cloud가 true이므로 C 모델 실행")
        task_c = asyncio.create_task(
            invoke_bedrock_model(4000, model_c_sysPrompt, model_result)
        )
    else:
        print("requires_cloud가 false이므로 C 모델 실행 안함")
    
    # D 모델 시작
    task_d = asyncio.create_task(
        invoke_bedrock_model(2000, model_d_sysPrompt, model_result)
    )
    
    # D의 결과 기다리기
    model_d_result = await task_d
    results['modelD'] = model_d_result
    
    print("D 완료, E와 F 시작")
    
    # D의 결과를 가지고 E와 F 시작
    task_e = asyncio.create_task(
        invoke_bedrock_model(4000, model_e_sysPrompt, model_d_result)
    )
    task_f = asyncio.create_task(
        invoke_bedrock_model(3500, model_f_sysPrompt, model_d_result)
    )
    
    # 모든 결과 대기
    #results['modelB'] = await task_b
    
    # C 모델은 requires_cloud가 true일 경우에만 실행되었으므로, 결과도 조건부로 저장
    if task_c:
        results['modelC'] = await task_c

    else:
        results['modelC'] = "모델 C는 실행되지 않았습니다 (requires_cloud가 false)"
    
    results['modelE'] = await task_e
    results['modelF'] = await task_f
    
    print("모든 모델 호출 완료")
    
    return results

def invoke_lambda_function(results):
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
        return "동작완료"
        #lambda_response = invoke_lambda_function(results)
        #return lambda_response
        
    
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

def extract_requires_cloud(text_input):
    try:
        # JSON 문자열인 경우 처리
        if text_input.strip().startswith('{') and text_input.strip().endswith('}'):
            data = json.loads(text_input)
            if "MODEL_DATA" in data:
                return data["MODEL_DATA"].get("requires_cloud", False)
        
        # 정규식으로 추출 시도
        requires_cloud_match = re.search(r'"requires_cloud"\s*:\s*(true|false)', text_input, re.IGNORECASE)
        if requires_cloud_match:
            requires_cloud_value = requires_cloud_match.group(1).lower()
            return (requires_cloud_value == 'true')
        
    except Exception as e:
        print(f"requires_cloud 추출 오류: {str(e)}")
    
    return False

# 테스트용 코드 (실제 사용 시 제거)
# if __name__ == "__main__":
#     # 테스트용 model_result 텍스트 예시
#     test_model_result_text = """
#     "MODEL_DATA":{"service_summary":"HealthConnect는 환자와 의사를 실시간으로 연결하고 원격 진료 및 건강 모니터링을 제공하는 플랫폼입니다.","requirements":{"functional":["실시간 화상 진료 세션","환자 건강 기록 관리 및 공유","처방전 디지털 발급 및 약국 연계","웨어러블 기기 연동 건강 데이터 수집"]},"architecture":{"pattern":"마이크로서비스 아키텍처","components":[{"name":"사용자 인증 서비스","purpose":"사용자 인증 및 권한 관리","tech_stack":"Node.js, JWT"},{"name":"화상 진료 서비스","purpose":"실시간 화상 통화 관리","tech_stack":"WebRTC, Socket.io"},{"name":"건강 기록 관리 서비스","purpose":"환자 건강 기록 저장 및 관리","tech_stack":"Node.js, MongoDB"},{"name":"처방전 관리 서비스","purpose":"디지털 처방전 발급 및 관리","tech_stack":"Node.js, MongoDB"},{"name":"데이터 수집 서비스","purpose":"웨어러블 기기 데이터 수집 및 처리","tech_stack":"AWS Kinesis, Lambda"}]},"tech_stack":{"frontend":["Flutter","WebRTC","Provider"],"backend":["Node.js","Express.js","Socket.io","gRPC"],"database":["MongoDB","Redis"],"infrastructure":["AWS EC2","ECS","API Gateway","Kinesis","S3","CloudFront","Lambda"]},"data_flow":"클라이언트 요청 → API 게이트웨이 → 마이크로서비스 → 데이터 처리/저장 → Kinesis를 통한 실시간 데이터 처리 → 클라이언트 응답","requires_cloud":true}
#     """

#     root_directory = os.path.abspath(os.sep)
#     print(root_directory)

#     current_directory = os.getcwd()
#     print("Current working directory:", current_directory)
    
#     # 함수 테스트
#     response = get_bedrock_response(test_model_result_text)
#     print(f"최종 응답: {response}")