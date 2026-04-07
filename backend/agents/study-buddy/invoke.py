import boto3
import json

AGENT_RUNTIME_ARN = "arn:aws:bedrock-agentcore:us-east-1:965116670064:runtime/StudyBuddy20e4cb-gjBg0z9G8l"
SESSION_ID = "study-buddy-local-test-session-001"

client = boto3.client("bedrock-agentcore", region_name="us-east-1")

payload = json.dumps({
    "request": "Explain machine learning in simple terms",
    "session_id": SESSION_ID,
})

print(f"Session ID: {SESSION_ID}")
print("Invoking agent...\n")

response = client.invoke_agent_runtime(
    agentRuntimeArn=AGENT_RUNTIME_ARN,
    runtimeSessionId=SESSION_ID,
    payload=payload,
)

response_body = response["response"].read()
response_data = json.loads(response_body)

print("Agent Response:")
print(response_data.get("response", response_data))
