import json
import urllib.request
import urllib.error

# APIのURL
API_URL = "https://098f-34-16-181-122.ngrok-free.app"  

def lambda_handler(event, context):
    try:
        print("Received event:", json.dumps(event))
        
        # Cognitoで認証されたユーザー情報を取得
        user_info = None
        if 'requestContext' in event and 'authorizer' in event['requestContext']:
            user_info = event['requestContext']['authorizer']['claims']
            print(f"Authenticated user: {user_info.get('email') or user_info.get('cognito:username')}")
        
        # リクエストボディの解析
        body = json.loads(event['body'])
        message = body['message']
        conversation_history = body.get('conversationHistory', [])
        
        print("Processing message:", message)
        print("Using custom API:", API_URL)
        
        # 会話履歴を使用
        messages = conversation_history.copy()
        
        # ユーザーメッセージを追加
        messages.append({
            "role": "user",
            "content": message
        })
        
        # カスタムAPIリクエストの準備
        data = json.dumps({
            "prompt": message,  
            "max_new_tokens": 512,
            "temperature": 0.7,
            "top_p": 0.9
        }).encode('utf-8')
        
        # APIリクエスト送信
        req = urllib.request.Request(
            f"{API_URL}/generate",
            data=data,
            headers={'Content-Type': 'application/json'}
        )
        
        # レスポンス処理
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read())
            assistant_response = result.get('generated_text', '')
        
        print("API response:", assistant_response)
        
        # アシスタントの応答を会話履歴に追加
        messages.append({
            "role": "assistant",
            "content": assistant_response
        })
        
        # 成功レスポンスの返却 - 元のフォーマットを維持
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({
                "success": True,
                "response": assistant_response,
                "conversationHistory": messages
            })
        }
        
    except urllib.error.URLError as e:
        print("API connection error:", str(e))
        return error_response(f"APIに接続できませんでした: {str(e)}")
    except Exception as error:
        print("Error:", str(error))
        return error_response(str(error))

def error_response(error_message):
    return {
        "statusCode": 500,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
            "Access-Control-Allow-Methods": "OPTIONS,POST"
        },
        "body": json.dumps({
            "success": False,
            "error": error_message
        })
    }
