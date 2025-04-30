import boto3
import json

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
            decoded_body = raw_body.decode("utf-8")  # byte → string

        except json.JSONDecodeError as e:
                print(f"JSON 파싱 오류: {e}")   
                # 줄 번호와 위치 확인
                print(f"오류 위치: 줄 {e.lineno}, 컬럼 {e.colno}")
                print(f"오류 부분: {e.doc[e.pos-20:e.pos+20]}")
        except:
            user_response = ""
            model_data = ""
            print("json 파싱 실패")

        return decoded_body


"""
modelA : 
{'ResponseMetadata': {'RequestId': 'c62a9b01-50e3-49bc-90c0-8ba8a7a6e04a', 'HTTPStatusCode': 200, 'HTTPHeaders': {'date': 'Wed, 30 Apr 2025 06:14:45 GMT', 'content-type': 'application/json', 'content-length': '8523', 'connection': 'keep-alive', 'x-amzn-requestid': 'c62a9b01-50e3-49bc-90c0-8ba8a7a6e04a', 'x-amzn-bedrock-invocation-latency': '44155', 'x-amzn-bedrock-output-token-count': '2901', 'x-amzn-bedrock-input-token-count': '1931'}, 'RetryAttempts': 0}, 'contentType': 'application/json', 'body': <botocore.response.StreamingBody object at 0x76e6c4dc3340>}
============================
함수호출
modelA : 
{'ResponseMetadata': {'RequestId': '678d9c51-ee1b-4a7c-9396-a40233f05222', 'HTTPStatusCode': 200, 'HTTPHeaders': {'date': 'Wed, 30 Apr 2025 06:14:54 GMT', 'content-type': 'application/json', 'content-length': '2403', 'connection': 'keep-alive', 'x-amzn-requestid': '678d9c51-ee1b-4a7c-9396-a40233f05222', 'x-amzn-bedrock-invocation-latency': '9213', 'x-amzn-bedrock-output-token-count': '647', 'x-amzn-bedrock-input-token-count': '1470'}, 'RetryAttempts': 0}, 'contentType': 'application/json', 'body': <botocore.response.StreamingBody object at 0x76e6c4dc3be0>}
============================
함수호출
WARNING:  StatReload detected changes in 'service/bedrockService.py'. Reloading...
modelA : 
{'ResponseMetadata': {'RequestId': '7e1343f3-a7a9-41c4-baae-202788e01e3a', 'HTTPStatusCode': 200, 'HTTPHeaders': {'date': 'Wed, 30 Apr 2025 06:16:34 GMT', 'content-type': 'application/json', 'content-length': '8307', 'connection': 'keep-alive', 'x-amzn-requestid': '7e1343f3-a7a9-41c4-baae-202788e01e3a', 'x-amzn-bedrock-invocation-latency': '39155', 'x-amzn-bedrock-output-token-count': '2608', 'x-amzn-bedrock-input-token-count': '3214'}, 'RetryAttempts': 1}, 'contentType': 'application/json', 'body': <botocore.response.StreamingBody object at 0x76e6c4db4f40>}
============================
함수호출
modelA : 
{'ResponseMetadata': {'RequestId': '4172bbe5-d9dd-49c3-a6eb-286b469af9e5', 'HTTPStatusCode': 200, 'HTTPHeaders': {'date': 'Wed, 30 Apr 2025 06:17:19 GMT', 'content-type': 'application/json', 'content-length': '7580', 'connection': 'keep-alive', 'x-amzn-requestid': '4172bbe5-d9dd-49c3-a6eb-286b469af9e5', 'x-amzn-bedrock-invocation-latency': '44787', 'x-amzn-bedrock-output-token-count': '2738', 'x-amzn-bedrock-input-token-count': '3814'}, 'RetryAttempts': 0}, 'contentType': 'application/json', 'body': <botocore.response.StreamingBody object at 0x76e6c4db49d0>}
============================
"""