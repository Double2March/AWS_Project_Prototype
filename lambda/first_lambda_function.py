import json

def lambda_handler(event, context):
    """
    첫 번째 람다 함수: 사용자 메시지를 빠르게 처리하여 결과를 반환
    """
    try:
        # 입력 메시지 추출
        message = event.get('message', '')
        username = event.get('username', 'Unknown')
        
        # 간단한 메시지 처리 (예시)
        result = f"{username}님의 메시지 '{message}'를 받았습니다. 처리 중입니다..."
        
        # 실제 애플리케이션에서는 여기에 필요한 비즈니스 로직을 추가하세요
        # 예: 텍스트 분석, 데이터베이스 조회 등
        
        return {
            'statusCode': 200,
            'result': result
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'result': f"오류 발생: {str(e)}"
        }