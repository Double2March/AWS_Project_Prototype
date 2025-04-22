# third_lambda_function.py
import json
import time
import random

def lambda_handler(event, context):
    """
    세 번째 람다 함수: 병렬 처리를 통한 추가 분석 수행
    """
    try:
        # 입력 메시지 추출
        message = event.get('message', '')
        username = event.get('username', 'Unknown')
        first_lambda_result = event.get('first_lambda_result', '')
        
        # 시간이 걸리는 작업 시뮬레이션
        time.sleep(1.5)  # 실제 환경에서는 처리 시간이 걸리는 로직으로 대체
        
        # 메시지에 대한 추가 분석 수행
        detailed_analysis = {
            "original_message": message,
            "username": username,
            "first_lambda_input": first_lambda_result,
            "detailed_analysis": {
                "topic_classification": classify_topic(message),  # 실제로는 토픽 분류 알고리즘 사용
                "intent_detection": detect_intent(message),      # 실제로는 의도 분석 알고리즘 사용
                "key_entities": extract_entities(message)        # 실제로는 개체명 인식 알고리즘 사용
            },
            "statistical_data": generate_dummy_stats()  # 실제로는 실제 통계 데이터 사용
        }
        
        return {
            'statusCode': 200,
            'result': json.dumps(detailed_analysis, ensure_ascii=False)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'result': f"오류 발생: {str(e)}"
        }

def classify_topic(text):
    """간단한 더미 토픽 분류 (실제 프로덕션에서는 ML 모델 사용)"""
    topics = ["기술 지원", "일반 문의", "제품 정보", "불만 사항", "칭찬", "기타"]
    
    # 실제로는 텍스트 분석을 통해 토픽을 결정하겠지만 예시를 위해 랜덤하게 선택
    if "도움" in text or "질문" in text:
        return "일반 문의"
    elif "오류" in text or "문제" in text or "안 됨" in text:
        return "기술 지원"
    elif "제품" in text or "서비스" in text:
        return "제품 정보"
    elif "실망" in text or "불만" in text or "안좋" in text:
        return "불만 사항"
    elif "좋아" in text or "감사" in text or "훌륭" in text:
        return "칭찬"
    else:
        return random.choice(topics)

def detect_intent(text):
    """간단한 더미 의도 감지 (실제 프로덕션에서는 NLU 모델 사용)"""
    intents = ["정보 요청", "도움 요청", "불만 표현", "피드백 제공", "일반 대화"]
    
    # 실제로는 NLU를 통해 의도를 분석하겠지만 예시를 위해 간단한 규칙 사용
    if "?" in text or "어떻게" in text or "무엇" in text:
        return "정보 요청"
    elif "도와" in text or "도움" in text:
        return "도움 요청"
    elif "안좋" in text or "최악" in text or "실망" in text:
        return "불만 표현"
    elif "생각" in text or "느낌" in text or "의견" in text:
        return "피드백 제공"
    else:
        return "일반 대화"

def extract_entities(text):
    """간단한 더미 개체명 추출 (실제 프로덕션에서는 NER 모델 사용)"""
    #