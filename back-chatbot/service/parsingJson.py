import json
import re

def parse_model_data(text_input):
    """
    텍스트 입력에서 MODEL_DATA를 파싱하여 필요한 데이터를 추출합니다.
    
    Args:
        text_input (str): 파싱할 텍스트 입력
        
    Returns:
        dict: 파싱된 데이터가 포함된 딕셔너리
        {
            'model_data': 전체 MODEL_DATA 딕셔너리,
            'requires_cloud': requires_cloud 값 (True/False),
            'service_summary': 서비스 요약,
            'architecture': 아키텍처 정보 딕셔너리,
            'tech_stack': 기술 스택 정보 딕셔너리
        }
    """
    result = {
        'model_data': {},
        'requires_cloud': False,
        'service_summary': '정보 없음',
        'architecture': {},
        'tech_stack': {}
    }
    
    try:
        # JSON 문자열인 경우 처리
        if text_input.strip().startswith('{') and text_input.strip().endswith('}'):
            data = json.loads(text_input)
            if "MODEL_DATA" in data:
                model_data = data["MODEL_DATA"]
                result['model_data'] = model_data
                result['requires_cloud'] = model_data.get("requires_cloud", False)
                result['service_summary'] = model_data.get("service_summary", "정보 없음")
                result['architecture'] = model_data.get("architecture", {})
                result['tech_stack'] = model_data.get("tech_stack", {})
                return result
        
        # MODEL_DATA 부분만 텍스트로 제공된 경우
        if text_input.strip().startswith('"MODEL_DATA"'):
            # MODEL_DATA 부분을 JSON 객체로 변환
            fixed_text = "{" + text_input + "}"
            try:
                data = json.loads(fixed_text)
                if "MODEL_DATA" in data:
                    model_data = data["MODEL_DATA"]
                    result['model_data'] = model_data
                    result['requires_cloud'] = model_data.get("requires_cloud", False)
                    result['service_summary'] = model_data.get("service_summary", "정보 없음")
                    result['architecture'] = model_data.get("architecture", {})
                    result['tech_stack'] = model_data.get("tech_stack", {})
                    return result
            except json.JSONDecodeError:
                # JSON 변환 실패 시, 정규식으로 추출 시도
                pass
        
        # 정규식을 사용하여 데이터 추출 시도
        # requires_cloud 값 추출
        requires_cloud_match = re.search(r'"requires_cloud"\s*:\s*(true|false)', text_input, re.IGNORECASE)
        if requires_cloud_match:
            requires_cloud_value = requires_cloud_match.group(1).lower()
            result['requires_cloud'] = (requires_cloud_value == 'true')
        
        # service_summary 추출
        service_summary_match = re.search(r'"service_summary"\s*:\s*"([^"]+)"', text_input)
        if service_summary_match:
            result['service_summary'] = service_summary_match.group(1)
        
        # architecture 및 tech_stack 추출은 복잡하므로 생략
        
    except Exception as e:
        print(f"JSON 파싱 오류: {str(e)}")
    
    return result

def extract_requires_cloud(text_input):
    """
    텍스트 입력에서 requires_cloud 값만 빠르게 추출합니다.
    
    Args:
        text_input (str): 파싱할 텍스트 입력
        
    Returns:
        bool: requires_cloud 값 (기본값: False)
    """
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