# Slack Bot Readme

## Steps to run app.py

### Step 1: Create an API Key
Create an API key under your IBM Cloud account [here](https://cloud.ibm.com/iam/apikeys).

### Step 2: Generate IAM Token
Copy the API key you created and use it to generate the IAM token with the following command, replacing `$api_key` with your actual API key:
```bash
curl -k -X POST --header "Content-Type: application/x-www-form-urlencoded" --header "Accept: application/json" --data-urlencode "grant_type=urn:ibm:params:oauth:grant-type:apikey" --data-urlencode "apikey=$api_key" "https://iam.cloud.ibm.com/identity/token"
```
### Step 3: Update app.py
Update the app.py file in your project with the generated IAM token as the bearer token.

### Step 4: Create a Sandbox Project
Create a sandbox project in IBM Cloud Data Platform.

<img width="1792" alt="Screenshot 2024-04-26 at 8 47 33 AM" src="https://media.github.ibm.com/user/7993/files/1a4f6e04-f212-462c-8ab4-1432f4d63d70">


### Step 5: Copy Project ID
Launch the prompt lab in your sandbox project and copy the project ID.
<img width="1792" alt="Screenshot 2024-04-26 at 8 48 53 AM" src="https://media.github.ibm.com/user/7993/files/09fe4992-37c2-42da-ac6f-c06d9097a81d">

### Step 6: Run app.py
```
python app.py "can you write a simple hello world program"
```

## Additional Notes
Include any additional notes or information here.

Feel free to customize it further based on project's specific details or add any additional information you think is necessary!
