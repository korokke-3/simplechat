import json
import os
import urllib.request
import re

# FastAPI推論エンドポイント
FASTAPI_ENDPOINT = "https://cc6f-34-125-141-228.ngrok-free.app/predict"

def lambda_handler(event, context):
    try:
        print("Received event:", json.dumps(event))

        # リクエストボディの解析
        body = json.loads(event['body'])
        message = body['message']  # ユーザーの入力メッセージ
        conversation_history = body.get('conversationHistory', [])

        # 会話履歴を1つのプロンプトに結合
        prompt = ""
        for msg in conversation_history:
            role = msg["role"]
            content = msg["content"]
            prompt += f"{role}: {content}\n"
        prompt += f"user: {message}\nassistant:"

        print("Sending prompt to FastAPI:", prompt)

        # FastAPIに送るリクエストペイロード
        payload = {
            "prompt": prompt,
            "max_new_tokens": 512,
            "do_sample": True,
            "temperature": 0.7,
            "top_p": 0.9
        }

        # HTTP POSTリクエストの作成
        req = urllib.request.Request(
            url=FASTAPI_ENDPOINT,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )

        # FastAPIからのレスポンス取得
        with urllib.request.urlopen(req) as response:
            response_body = json.loads(response.read().decode())
            print("Response from FastAPI:", json.dumps(response_body))

        # FastAPIの出力から生成されたテキストを取り出す
        assistant_response = response_body["generated_text"]

        # 新しい会話履歴を更新
        updated_history = conversation_history + [
            {"role": "user", "content": message},
            {"role": "assistant", "content": assistant_response}
        ]

        # Lambdaのレスポンス
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
                "conversationHistory": updated_history
            })
        }

    except Exception as error:
        print("Error:", str(error))
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
                "error": str(error)
            })
        }
