# StudyBuddy AI

AI-powered educational tutor built on AWS Bedrock AgentCore Runtime with real-time WebSocket streaming and conversation memory.

## Architecture

```
┌─────────────────┐         ┌──────────────────────┐         ┌──────────────────────────┐
│   React UI      │────────▶│  API Gateway (REST)  │────────▶│ WebSocketConnectFunction │
│  (Cognito Auth) │         │ + Cognito Authorizer │         │  (SigV4 presigned URL)   │
└────────┬────────┘         └──────────────────────┘         └──────────────────────────┘
         │
         │  WebSocket (SigV4 presigned URL)
         ▼
┌──────────────────────────────────┐         ┌───────────────────┐
│  AgentCore Runtime               │────────▶│  AgentCore Memory │
│  (Strands Agent + Bedrock LLM)   │         │  (Persistence)    │
└──────────────────────────────────┘         └───────────────────┘
         ▲
         │  HTTP invoke (synchronous)
         │
┌────────┴─────────────────────────┐         ┌───────────────────────────┐
│  AgentCoreInvokeFunction         │◀────────│  Step Functions Workflow  │
│  (Lambda - direct invocation)    │         │  (query-processing)       │
└──────────────────────────────────┘         └───────────────────────────┘
```

There are two paths into the agent:

1. **WebSocket (used by the UI):** The React frontend authenticates with Cognito, requests a SigV4 presigned WebSocket URL from the backend Lambda, then connects directly to AgentCore Runtime. The agent streams responses back in real time.

2. **HTTP entrypoint (via Step Functions):** The `AgentCoreInvokeFunction` Lambda calls the agent's `@app.entrypoint` handler synchronously. This Lambda can be invoked directly or orchestrated by the Step Functions `query-processing` workflow, which adds retry logic, timeouts, and error handling.

### Authentication Flow

1. User signs in via Cognito (email + password → JWT tokens)
2. JWT authenticates the `POST /websocket/connect` REST API call
3. Lambda generates a SigV4 presigned WebSocket URL (5-min expiry) using its IAM role
4. Browser connects directly to AgentCore Runtime via the presigned URL
5. User identity is passed as a custom header query parameter in the presigned URL
6. Agent streams responses back over the WebSocket connection

### Agent Details

- **Framework:** [Strands Agents](https://github.com/strands-agents/strands-agents) (Python)
- **Model:** Amazon Nova Lite (`us.amazon.nova-lite-v1:0` by default, configurable)
- **Memory:** AgentCore Memory (short-term, 30-day event expiry, per-session + per-user)
- **Tools:** `current_time`
- **System prompt:** Spanish-language educational tutor persona with Markdown formatting
- **Handlers:**
  - `@app.websocket` — real-time streaming for the UI
  - `@app.entrypoint` — synchronous HTTP invocation for Lambda/Step Functions

## Project Structure

```
backend/
  agents/study-buddy/
    agent.py              # Agent: WebSocket handler + HTTP entrypoint
    invoke.py             # Test script for direct invocation via boto3
    requirements.txt      # Python deps (strands-agents, bedrock-agentcore, pydantic)
  functions/
    websocket-connect.js  # Lambda: generates SigV4 presigned WebSocket URL
    agentcore-invoke.js   # Lambda: synchronous HTTP invocation of AgentCore Runtime
  workflows/
    query-processing.asl.json  # Step Functions: orchestrates agentcore-invoke with retries
  template.yaml           # SAM template (API GW, Lambdas, Cognito, AgentCore Runtime/Memory)
  openapi.yaml            # OpenAPI spec with Cognito authorizer definition
  samconfig.yaml.template # SAM deploy config template

frontend/
  src/
    components/
      Chat.tsx            # Real-time chat with WebSocket streaming + Markdown rendering
      Home.tsx            # Landing page with example queries
      Login.tsx           # Cognito sign-in form
      Signup.tsx          # Cognito sign-up + email verification
      Layout.tsx          # App shell with navigation
      Navigation.tsx      # Top nav bar
      UserMenu.tsx        # User dropdown (sign out)
      ProtectedRoute.tsx  # Auth guard for protected routes
    contexts/
      AuthContext.tsx      # React context for auth state
    services/
      websocket.ts        # WebSocket client (presigned URL connection, event emitter)
      api.ts              # REST client (presigned URL request, query endpoint)
      auth.ts             # Cognito auth service (sign-in/up/out, tokens, password reset)
      userService.ts      # User ID management
    config/
      api.ts              # API base URL + endpoint config
  template.yaml           # SAM template (S3 bucket + CloudFront distribution)
  scripts/
    build-with-api-config.sh   # Fetches backend stack outputs, injects env vars, builds
    generate-samconfig.sh      # Generates samconfig.yaml from template
  samconfig.yaml.template      # SAM deploy config template

setup-local-dev.sh        # One-command local dev setup (prereqs, deploy, configure)
```

## Getting Started

### Prerequisites

- Node.js 18+
- AWS CLI (configured with credentials)
- SAM CLI
- An AWS account with Bedrock model access enabled

### Quick Start

```bash
./setup-local-dev.sh
```

This script checks prerequisites, optionally deploys the backend stack, fetches CloudFormation outputs, generates a `.env.local` for the frontend, and installs dependencies.

### Manual Setup

```bash
# 1. Deploy backend
cd backend
sam build
sam deploy --guided
# Note the stack outputs (API URL, User Pool ID, Client ID)

# 2. Configure and run frontend
cd ../frontend
npm install

# Create .env.local with values from backend stack outputs:
cat > .env.local << EOF
VITE_API_BASE_URL=https://<api-id>.execute-api.<region>.amazonaws.com/api/
VITE_USER_POOL_ID=<user-pool-id>
VITE_USER_POOL_CLIENT_ID=<client-id>
VITE_AWS_REGION=us-east-1
EOF

npm run dev

# 3. (Optional) Deploy frontend to S3 + CloudFront
cd frontend
./scripts/build-with-api-config.sh
sam build
sam deploy --guided
# Upload dist/ to the S3 bucket from stack outputs
```

### CI/CD Build

The `build-with-api-config.sh` script automates the frontend build by pulling config from the deployed backend stack:

```bash
cd frontend
BACKEND_STACK_NAME=studybuddy-ai-backend-dev \
AWS_REGION=us-east-1 \
./scripts/build-with-api-config.sh
```

## Environment Variables

### Backend Agent (set via SAM template)

| Variable | Required | Default | Description |
|---|---|---|---|
| `AGENTCORE_MEMORY_ID` | Yes | — | AgentCore Memory resource ID |
| `AWS_REGION` | No | `us-east-1` | AWS region |
| `BEDROCK_MODEL_ID` | No | `us.amazon.nova-lite-v1:0` | Bedrock model ID |
| `AGENT_RUNTIME_ARN` | Yes | — | AgentCore Runtime ARN (auto-set by SAM) |

### Frontend (`.env.local`)

| Variable | Required | Description |
|---|---|---|
| `VITE_API_BASE_URL` | Yes | Backend API Gateway endpoint URL |
| `VITE_USER_POOL_ID` | Yes | Cognito User Pool ID |
| `VITE_USER_POOL_CLIENT_ID` | Yes | Cognito App Client ID |
| `VITE_AWS_REGION` | No | AWS region (used by Cognito SDK) |

## AWS Resources Created

### Backend Stack

- **API Gateway** (REST) with Cognito authorizer
- **Lambda Functions:**
  - `WebSocketConnectFunction` — presigned URL generation (Node.js 24.x, ARM64)
  - `AgentCoreInvokeFunction` — synchronous agent invocation (Node.js 24.x, ARM64, 600s timeout)
- **AgentCore Runtime** — runs the Strands agent (Python 3.13, public network)
- **AgentCore Memory** — short-term conversation persistence (30-day event expiry)
- **Cognito User Pool + Client** — email-based auth, SRP + password flows
- **IAM Role** — AgentCore execution role (Bedrock model invocation, memory, logging, X-Ray)
- **Step Functions State Machine** — `query-processing` workflow (defined in ASL, not wired in SAM yet)

### Frontend Stack

- **S3 Bucket** — static site hosting (versioned, private, 30-day old version cleanup)
- **CloudFront Distribution** — HTTPS, OAC for S3, SPA error routing (403/404 → index.html)

## Step Functions Workflow

The `query-processing.asl.json` workflow orchestrates the `AgentCoreInvokeFunction` Lambda:

- **Input:** `{ sessionId, userId, request }`
- **Retries:** 3 attempts with exponential backoff for Lambda service errors
- **Timeouts:** 600s per invocation, 900s total workflow
- **Error handling:** Separate paths for timeout vs general errors
- **Output:** `{ sessionId, request, response, status }`

This is useful for async or batch invocations where you don't need real-time streaming.

## API Endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| `POST` | `/websocket/connect` | Cognito JWT | Returns a SigV4 presigned WebSocket URL for AgentCore Runtime |

### WebSocket Message Protocol

**Client → Agent:**
```json
{ "request": "your question", "session_id": "uuid", "user_id": "cognito-sub" }
```

**Agent → Client (streaming):**
```json
{ "type": "stream_event", "event": { "data": "text chunk" } }
{ "type": "stream_event", "event": { "current_tool_use": { "name": "current_time" } } }
{ "type": "stream_event", "event": { "complete": true } }
{ "type": "complete", "session_id": "uuid" }
```

## Testing the Agent Directly

You can invoke the agent outside the UI using the test script:

```bash
cd backend/agents/study-buddy
pip install -r requirements.txt
python invoke.py
```

This calls `InvokeAgentRuntime` via boto3, hitting the `@app.entrypoint` handler synchronously.
