from flask import Flask, request, jsonify
import requests
import os
import subprocess
import json

app = Flask(__name__)

def get_bearer_token(apikey):
    # Generate the bearer token using curl command
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
    apikey = os.environ.get('API_KEY')  # Retrieve API key from environment variable
    if not apikey:
        print("API key not found in environment variable.")
        return None

    # Generate bearer token
    token = get_bearer_token(apikey)
    if not token:
        return None

    # Modify this function to call the Watson ML API for text generation
    url = "https://us-south.ml.cloud.ibm.com/ml/v1/text/generation?version=2023-05-29"
    # Construct the request body
    body = {
        "input": input_text,
        "parameters": {
            "decoding_method": "greedy",
            "max_new_tokens": 900,
            "repetition_penalty": 1
        },
        "model_id": "meta-llama/llama-3-8b-instruct",
        "project_id": "2ea1b7a7-c453-421f-88b7-97ac55bd90e3"
    }
    # Add your Watson ML API authorization token to the headers
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

        return jsonify({
            "text": f"**Input:** {input_text}\n**Output:** {generated_text}\n**Confidence:** {confidence}\n**Response Code:** {response_code}"
        })
    else:
        return jsonify({"text": "No response received from the API."})

if __name__ == "__main__":
    app.run(debug=False)
