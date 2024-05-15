from flask import Flask, request, jsonify
from slack_sdk import WebClient
import requests
import slack
import os
import subprocess
import json
import string
from slackeventsapi import SlackEventAdapter
import time

app = Flask(__name__)

slack_token = os.getenv("SLACK_TOKEN")
if not slack_token:
    raise ValueError("Slack API token not found.")
client = WebClient(token=slack_token)

signing_secret = os.getenv("SIGNING_SECRET")
if not signing_secret:
    raise ValueError("Slack signing secret not found.")
slack_events_adapter = SlackEventAdapter(signing_secret, "/events-endpoint", app)

BOT_ID = client.api_call("auth.test")['user_id']

BAD_WORDS = ['hmm', 'no', 'idiot']

def get_bearer_token(apikey):
    curl_command = f'curl -k -X POST --header "Content-Type: application/x-www-form-urlencoded" --header "Accept: application/json" --data-urlencode "grant_type=urn:ibm:params:oauth:grant-type:apikey" --data-urlencode "apikey={apikey}" "https://iam.cloud.ibm.com/identity/token"'
    try:
        token_response = subprocess.check_output(curl_command, shell=True).decode('utf-8')
        token_json = json.loads(token_response)
        access_token = token_json.get('access_token')
        return access_token
    except subprocess.CalledProcessError as e:
        print(f"Error generating token: {e}")
        return None

def text_generation(input_text):
    apikey = os.environ.get('API_KEY')
    if not apikey:
        print("API key not found in environment variable.")
        return None

    token = get_bearer_token(apikey)
    if not token:
        return None

    url = "https://us-south.ml.cloud.ibm.com/ml/v1/text/generation?version=2023-05-29"
    body = {
        "input": input_text,
        "parameters": {
            "decoding_method": "greedy",
            "max_new_tokens": 900,
            "repetition_penalty": 1
        },
        "model_id": "meta-llama/llama-3-8b-instruct",
        "project_id": os.environ.get('PROJECT_ID')
    }
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}" 
    }

    try:
        response = requests.post(url, headers=headers, json=body)
        if response.status_code != 200:
            raise Exception("Non-200 response: " + str(response.text))
        return response.json()
    except Exception as e:
        print(f"Error: {e}")
        return None

@app.route('/generate_text', methods=['POST'])
def generate_text():
    input_text = request.form.get('text')
    if not input_text:
        return jsonify({"text": "Please provide input text."})

    response = text_generation(input_text)
    if response:
        generated_text = response.get('results', [{}])[0].get('generated_text', '')
        confidence = response.get('confidence', '')
        response_code = response.get('response_code', '')
        
        print(f"Generated Text: {generated_text}")

        return jsonify({"Response": generated_text})
    else:
        return jsonify({"text": "Error in text generation."})

def check_if_bad_words(message):
    msg = message.lower()
    msg = msg.translate(str.maketrans('', '', string.punctuation))

    return any(word in msg for word in BAD_WORDS)

processed_messages = set()

@slack_events_adapter.on('message')
def message(payload):
    event = payload.get('event', {})
    channel_id = event.get('channel')
    user_id = event.get('user')
    text = event.get('text')
    message_ts = event.get('ts')

    if BOT_ID != user_id and message_ts not in processed_messages:
        processed_messages.add(message_ts)

        generated_response = text_generation(text)
        if generated_response:
            generated_text = generated_response.get('results', [{}])[0].get('generated_text', '')
            confidence = generated_response.get('confidence', '')
            response_code = generated_response.get('response_code', '')
            print(f"Generated Text: {generated_text}")
            client.chat_postMessage(
                channel=channel_id,
                text=f"{generated_text}"
            )
        else:
            client.chat_postMessage(channel=channel_id, text="Error in text generation.")

        time.sleep(1)

@app.route("/events-endpoint", methods=["POST"])
def events_endpoint():
    print("Received POST request to /events-endpoint")
    return "", 200

if __name__ == "__main__":
    print("[INFO] Server listening")
    app.run(port=8080)
