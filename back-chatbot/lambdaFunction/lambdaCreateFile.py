import json
import os
import re
import shutil
import tempfile
import zipfile
import boto3
from datetime import datetime


def lambda_handler(event, context):

    try:
        print(f"이벤트 수신: {json.dumps(event, indent=2)}")
        
        # 모델 결과 추출
        model_results = event
        
        # modelE와 modelF 추출
        modelE = model_results.get('modelE')
        modelF = model_results.get('modelF')
        
        # modelC 추출 (있을 수도 있고 없을 수도 있음)
        modelC = model_results.get('modelC')
        
        # 필수 파라미터 검증
        if not modelE or not modelF:
            raise ValueError('필수 파라미터 modelE와 modelF가 누락되었습니다')

        # 서비스명 추출 - #SN# service: 서비스명#PS# 포맷에서 서비스명 획득
        service_name = "idea-maker"  # 기본값
        service_match = re.search(r"#SN#.*?service\s*:\s*([^\n\r#]+).*?#PS#", modelE, re.DOTALL)
        if service_match:
            service_name = service_match.group(1).strip()
            print(f"서비스명 추출: {service_name}")
            
        # README.md 내용 추출 (modelF에서) - user_response로 사용하기 위함
        readme_content = ""
        readme_match = re.search(r'#FB#\s*filename:\s*.*README\.md\s*#CB#\s*([\s\S]*?)#CE#', modelF)
        if readme_match:
            readme_content = readme_match.group(1).strip()
            print("README.md 내용 추출 성공")
        else:
            # README.md가 없을 경우 USER_RESPONSE를 찾아봄
            user_response_match = re.search(r'#PS#\s*USER_RESPONSE:\s*([\s\S]*?)(?=#PE#|$)', modelF)
            if user_response_match:
                readme_content = user_response_match.group(1).strip()
                print("USER_RESPONSE 내용 추출 성공")
            else:
                readme_content = f"{service_name} 파일이 성공적으로 처리되어 압축되었습니다."
                print("README 또는 USER_RESPONSE를 찾을 수 없어 기본 메시지 사용")

        # 파일 처리를 위한 임시 디렉토리 생성
        temp_dir = tempfile.mkdtemp(prefix=f"{service_name}-")
        print(f"임시 디렉토리 생성: {temp_dir}")

        # 파일저장
        process_file_content(modelE, temp_dir)
        process_file_content(modelF, temp_dir)
        
        # modelC 처리 (있는 경우만)
        if modelC and modelC != "no data":
            print("modelC 데이터를 처리합니다...")
            process_file_content(modelC, temp_dir)
        else:
            print("modelC 데이터가 없습니다.")
        
        # ZIP 파일 생성 - 서비스명 사용
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        zip_filename = f"{service_name}-{timestamp}.zip"
        zip_filepath = os.path.join(temp_dir, zip_filename)
        create_zip_file(temp_dir, zip_filepath)
        
        # S3에 업로드 및 presigned URL 생성
        presigned_url = upload_to_s3_and_get_presigned_url(zip_filepath, zip_filename)
        
        # 임시 파일 정리
        cleanup_temp_files(temp_dir)
        
        user_response = readme_content
        presigned_urls = [presigned_url]
        
        return [user_response, presigned_urls]
        
    except Exception as e:
        print(f"파일 처리 오류: {str(e)}")
        return [f"파일 처리 중 오류가 발생했습니다: {str(e)}", [""]]


def process_file_content(content, base_dir):
    
    # 서비스명 마커는 파일로 처리하지 않고 건너뛰기
    # 내용에서 #SN# service: 서비스명#PS# 부분 건너뛰기
    content_without_service_name = re.sub(r'#SN#\s*service:\s*[^#\n]+#PS#\s*', '', content)
    
    # 내용에서 모든 파일 블록 찾기
    # #FB# (파일 시작), #CB# (내용 시작), #CE# (내용 끝) 마커를 찾음
    file_block_regex = r'#FB#\s*filename:\s*([^\n]+)\s*#CB#\s*([\s\S]*?)(?=#CE#|$)'
    
    for match in re.finditer(file_block_regex, content_without_service_name):
        file_path = match.group(1).strip()      # 파일 경로
        file_content = match.group(2).strip()   # 파일 내용
        
        # 전체 파일 경로 생성
        full_path = os.path.join(base_dir, file_path)
        
        # 디렉토리가 존재하지 않으면 생성
        dir_name = os.path.dirname(full_path)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
            print(f"디렉토리 생성: {dir_name}")
        
        # 파일 작성
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(file_content)
        print(f"파일 생성: {full_path}")
    
    # USER_RESPONSE 블록 처리 (modelF 구조용)
    user_response_regex = r'#PS#\s*USER_RESPONSE:\s*([\s\S]*?)(?=#PE#|$)'
    for match in re.finditer(user_response_regex, content):
        response_content = match.group(1).strip()
        response_path = os.path.join(base_dir, 'USER_RESPONSE.md')
        
        with open(response_path, 'w', encoding='utf-8') as f:
            f.write(response_content)
        print(f"USER_RESPONSE.md 생성됨")
    
    # PROVISIONING_SCRIPTS 블록 처리
    provisioning_scripts_regex = r'PROVISIONING_SCRIPTS:\s*(#FB#[\s\S]*?#CE#)'
    for match in re.finditer(provisioning_scripts_regex, content):
        # 스크립트 내용을 다시 처리 함수로 전달
        process_file_content(match.group(1), base_dir)
    
    # BUILD_SCRIPTS 블록 처리
    build_scripts_regex = r'BUILD_SCRIPTS:\s*(#FB#[\s\S]*?#CE#)'
    for match in re.finditer(build_scripts_regex, content):
        # 스크립트 내용을 다시 처리 함수로 전달
        process_file_content(match.group(1), base_dir)


def create_zip_file(source_dir, zip_filepath):

    zip_basename = os.path.basename(zip_filepath)
    
    with zipfile.ZipFile(zip_filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(source_dir):
            for file in files:
                file_path = os.path.join(root, file)
                
                # ZIP 파일 자체는 제외
                if file == zip_basename:
                    continue
                
                # ZIP 파일에 아카이브 경로 계산 (base_dir 상대 경로)
                archive_path = os.path.relpath(file_path, source_dir)
                zipf.write(file_path, archive_path)
    
    zip_size = os.path.getsize(zip_filepath)
    print(f"ZIP 파일 생성: {zip_filepath} ({zip_size} 바이트)")


def upload_to_s3_and_get_presigned_url(file_path, s3_key):

    s3 = boto3.client('s3')
    bucket_name = os.environ['S3_BUCKET_NAME']  # 없으면 KeyError 발생
    
    # S3에 업로드
    with open(file_path, 'rb') as file_data:
        s3.upload_fileobj(file_data, bucket_name, s3_key)
    
    print(f"S3에 파일 업로드: s3://{bucket_name}/{s3_key}")
    
    # Presigned URL 생성 (기본 15분 유효)
    presigned_url = s3.generate_presigned_url(
        'get_object',
        Params={
            'Bucket': bucket_name,
            'Key': s3_key
        },
        ExpiresIn=1800  # 15분 (초 단위)
    )
    
    print(f"Presigned URL 생성됨")
    return presigned_url


def cleanup_temp_files(temp_dir):
    try:
        shutil.rmtree(temp_dir)
        print(f"임시 디렉토리 정리: {temp_dir}")
    except Exception as e:
        print(f"임시 파일 정리 오류: {str(e)}")