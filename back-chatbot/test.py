import os
import re
import json
import asyncio
import boto3
import aioboto3

from botocore.exceptions import ClientError

from prompt.prompt_a import systemPrompt as model_a_sysPrompt
from prompt.prompt_b import systemPrompt as model_b_sysPrompt
from prompt.prompt_c import systemPrompt as model_c_sysPrompt
from prompt.prompt_d import systemPrompt as model_d_sysPrompt
from prompt.prompt_e import systemPrompt as model_e_sysPrompt
from prompt.prompt_f import systemPrompt as model_f_sysPrompt

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
    # 결과를 저장할 딕셔너리
    results = {}
    
    requires_cloud = parse_requires_cloud(model_result)
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
        results['modelC'] = "no data"
    
    results['modelE'] = await task_e
    results['modelF'] = await task_f
    
    print("모든 모델 호출 완료")

    print("\n\n\n")
    print(results['modelC'])
    print("\n\n\n")
    print(results['modelD'])
    print("\n\n\n")
    print(results['modelE'])
    print("\n\n\n")
    print(results['modelF'])
    print("\n\n\n")
    
    return results

def parse_requires_cloud(text):
    # 정규식으로 requires_cloud 값을 추출
    pattern = r'requires_cloud:\s*(true|false)'
    match = re.search(pattern, text, re.IGNORECASE)
    
    # 매치가 있으면 해당 값을 boolean으로 변환하여 반환
    if match and match.group(1):
        return match.group(1).lower() == 'true'
    
    # 매치가 없으면 기본값으로 False 반환
    return False

def invoke_lambda_function(results):
    # AWS Lambda 클라이언트 초기화
    lambda_client = boto3.client('lambda', region_name='ap-northeast-2')
    
    # Lambda 함수 호출
    response = lambda_client.invoke(
        FunctionName='arn:aws:lambda:ap-northeast-2:671957687853:function:idea-maker-create-file',
        InvocationType='RequestResponse',
        Payload=json.dumps(results)
    )
    
    # Lambda 응답 처리
    response_payload = json.loads(response['Payload'].read())
    return response_payload  # [user_response, presignedUrls] 형식의 응답 기대

#테스트용 코드 (실제 사용 시 제거)
if __name__ == "__main__":
    # 테스트용 model_result 텍스트 예시
    test_model_result_text = """
        service : TaskMaster
        service_summary: TaskMaster - 소규모 팀을 위한 직관적인 프로젝트 및 작업 관리 도구
        functional_requirements: 프로젝트 생성 및 작업 할당, 마감일 추적 및 알림 설정, 팀원 간 실시간 댓글 및 협업, 작업 완료율 및 팀 성과 대시보드
        architecture_pattern: 클라이언트-서버 아키텍처, 단일 페이지 애플리케이션(SPA)
        components: Vue.js 프론트엔드|사용자 인터페이스 및 상호작용|Vue.js, Django 백엔드|비즈니스 로직 및 데이터 처리|Django, PostgreSQL 데이터베이스|데이터 저장 및 관리|PostgreSQL
        frontend_tech: Vue.js, Vuex, Vue Router, axios
        backend_tech: Django, Django REST Framework, Django Channels
        database_tech: PostgreSQL
        infrastructure_tech: AWS EC2, AWS RDS, AWS S3, AWS CloudFront, AWS Route 53, AWS ELB
        data_flow_summary: 사용자 요청 → Vue.js → axios → Django → Django ORM → PostgreSQL, 실시간 업데이트: Django Channels → WebSocket → Vue.js
        requires_cloud: true
    """

    root_directory = os.path.abspath(os.sep)
    print(root_directory)

    current_directory = os.getcwd()
    print("Current working directory:", current_directory)
    
    # 함수 테스트
    response = get_bedrock_response(test_model_result_text)
    print(f"최종 응답: {response}")