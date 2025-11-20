# SAP AI Core Authentication with Microsoft Agent Framework

This sample demonstrates how to authenticate and interact with SAP AI Core using the Microsoft agent-framework.

## Prerequisites

- Python 3.8+
- SAP AI Core account with credentials
- Microsoft agent-framework installed

## Installation

```bash
pip install agent-framework requests python-dotenv
```

## Configuration

Create a `.env` file in this directory with your SAP AI Core credentials:

```env
AICORE_CLIENT_ID=your_client_id
AICORE_CLIENT_SECRET=your_client_secret
AICORE_AUTH_URL=https://your-auth-url.authentication.sap.hana.ondemand.com
AICORE_BASE_URL=https://api.ai.your-region.hana.ondemand.com
AICORE_RESOURCE_GROUP=default
AICORE_DEPLOYMENT_ID=your-deployment-id
```

## Examples

### 1. Basic Authentication (basic_auth.py)
Shows how to obtain OAuth2 token from SAP AI Core.

```bash
python basic_auth.py
```

### 2. Agent with SAP AI Core (agent_with_sap.py)
Demonstrates using an agent with SAP AI Core as a tool.

```bash
python agent_with_sap.py
```

### 3. Token Manager (token_manager.py)
Shows token refresh management with automatic expiration handling.

```bash
python token_manager_example.py
```

## File Structure

- `basic_auth.py` - Basic OAuth2 token retrieval
- `agent_with_sap.py` - Agent framework integration with SAP AI Core
- `token_manager.py` - Token refresh manager class
- `token_manager_example.py` - Example using the token manager
- `sap_client.py` - Complete SAP AI Core client wrapper
- `requirements.txt` - Python dependencies
- `.env.example` - Example environment variables

## How It Works

1. **Authentication**: Uses OAuth2 client credentials flow to obtain Bearer token
2. **Token Management**: Automatically refreshes tokens before expiration
3. **Agent Integration**: Wraps SAP AI Core as an MCP tool for the agent framework
4. **Headers**: Includes required `Authorization` and `AI-Resource-Group` headers

## Notes

- Tokens typically expire after 1 hour (3600 seconds)
- The token manager automatically refreshes 5 minutes before expiration
- SAP AI Core requires the `AI-Resource-Group` header for resource isolation
