import json
import time

def lambda_handler(event, context):
    """
    두 번째 람다 함수: 심층 분석 수행 (더 오래 걸리는 작업)
    """
    try:
        # 입력 메시지 추출
        message = event.get('message', '')
        username = event.get('username', 'Unknown')
        first_lambda_result = event.get('first_lambda_result', '')
        
        # 시간이 더 오래 걸리는 작업 시뮬레이션
        time.sleep(2)  # 실제 환경에서는 처리 시간이 걸리는 로직으로 대체
        
        # 첫 번째 람다 결과와 함께 더 심층적인 분석 수행
        analysis_result = {
            "original_message": message,
            "username": username,
            "first_lambda_analysis": first_lambda_result,
            "additional_analysis": {
                "word_count": len(message.split()),
                "character_count": len(message),
                "sentiment_score": calculate_dummy_sentiment(message)  # 실제로는 감정 분석 API 사용
            },
            "recommendations": generate_dummy_recommendations(message)  # 실제로는 추천 알고리즘 사용
        }
        
        return {
            'statusCode': 200,
            'result': json.dumps(analysis_result, ensure_ascii=False)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'result': f"오류 발생: {str(e)}"
        }

def calculate_dummy_sentiment(text):
    """간단한 더미 감정 분석 (실제 프로덕션에서는 ML 모델이나 API 사용)"""
    positive_words = ['좋아', '훌륭', '행복', '감사', '좋은', '멋진']
    negative_words = ['나쁜', '싫어', '화나', '실망', '안좋은', '최악']
    
    text_lower = text.lower()
    
    positive_count = sum(1 for word in positive_words if word in text_lower)
    negative_count = sum(1 for word in negative_words if word in text_lower)
    
    if positive_count > negative_count:
        return "긍정적"
    elif negative_count > positive_count:
        return "부정적"
    else:
        return "중립적"

def generate_dummy_recommendations(text):
    """간단한 더미 추천 생성 (실제 프로덕션에서는 추천 알고리즘 사용)"""
    if len(text) < 10:
        return ["더 자세한 정보를 제공해주세요", "질문을 구체적으로 해주세요"]
    elif "질문" in text:
        return ["FAQ 섹션을 확인해보세요", "관련 주제: 고객 지원, 기술 지원"]
    elif "도움" in text:
        return ["고객 지원팀에 문의해보세요", "관련 문서를 참조하세요"]
    else:
        return ["이 주제에 대한 추가 정보가 필요하시면 알려주세요", "관련 주제: 일반 정보"]