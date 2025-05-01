# dynamodb_manager.py
import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key

# DynamoDB 클라이언트 초기화
dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-2')
table = dynamodb.Table('idea_maker')

def put_model_data(uid, timestamp, model_data):
    try:
        # DynamoDB에 항목 저장
        item = {
            'id': str(uid),
            'timestamp': timestamp.isoformat(),
            'model_data': model_data
        }
        table.put_item(Item=item)
        print(str(timestamp) + " | Item saved successfully : "+ str(model_data))
    except ClientError as e:
        print(f"Error saving item: {e}")
        raise

def get_model_data(uid: str):
    try:
        response = table.query(
            KeyConditionExpression=Key('id').eq(str(uid)), 
            ScanIndexForward=False, 
            Limit=1
        )
        
        # 결과 처리
        if 'Items' in response and len(response['Items']) > 0:
            latest_item = response['Items'][0]
            model_data = latest_item['model_data']  # 최신 model_data
            return model_data
        else:
            return None  # 해당 uuid에 대한 데이터가 없으면 None 반환

    except Exception as e:
        print(f"Error retrieving data: {e}")
        return None