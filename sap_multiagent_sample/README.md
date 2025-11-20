# SAP Multi-Agent Sample

This sample demonstrates authentication and connectivity for SAP AI Core. It shows how to use SAP AI Core's Azure OpenAI-compatible API with proper OAuth2 token management.

## Overview

The sample provides:
- **SAPTokenManager**: Centralized OAuth2 token management with automatic refresh
- **Direct OpenAI Integration**: Using AsyncOpenAI client configured for SAP AI Core
- **Working Examples**: Proven patterns from the single-agent sample

## Status

✅ **Working**: Single-agent chat completions with tool calling (see `../sap_sample/token_manager_example.py`)  
⚠️ **In Progress**: Multi-agent workflows with Agent Framework

### Current Challenge

SAP AI Core requires an `api-version` query parameter in all requests. The Agent Framework's `OpenAIChatClient` and `AzureOpenAIChatClient` don't currently support custom query parameters via `default_query`. 

**Workaround**: Use the `openai.AsyncOpenAI` client directly with `default_query={"api-version": "2024-02-01"}` as shown in the working sample.

## Prerequisites

1. SAP AI Core subscription with deployed model (e.g., GPT-4)
2. OAuth2 credentials for SAP AI Core
3. Python 3.9+

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file with your SAP AI Core credentials:
```env
# SAP AI Core OAuth2 Configuration
AICORE_AUTH_URL=https://your-tenant.authentication.sap.hana.ondemand.com
AICORE_CLIENT_ID=your-client-id
AICORE_CLIENT_SECRET=your-client-secret

# SAP AI Core API Configuration
AICORE_BASE_URL=https://api.ai.your-region.sap.com
AICORE_RESOURCE_GROUP=default
AICORE_DEPLOYMENT_ID=your-deployment-id
```

## Authentication Design

### Token Management Strategy

The sample uses a **centralized token manager** approach:

1. **SAPTokenManager Class**:
   - Singleton pattern for token lifecycle management
   - Thread-safe token refresh with locking
   - Automatic token refresh before expiration
   - Provides authentication headers for all agents

2. **Integration with Agents**:
   - Each agent receives the same token manager instance
   - Token is refreshed transparently during long-running workflows
   - No need to manage tokens at the agent level

3. **Benefits**:
   - Single point of authentication
   - Reduced token refresh calls
   - Consistent authentication across all agents
   - Simplified error handling

## Running the Samples

### Working Example: Single Agent with Tools
```bash
cd ../sap_sample
python token_manager_example.py
```

This demonstrates:
- OAuth2 token management
- Chat completions
- Tool/function calling
- Proper SAP AI Core API usage

### Test Connectivity
```bash
python test_simple.py
```

Verifies that you can connect to SAP AI Core and make successful API calls.

### Future: Multi-Agent Workflows
The `multiagent_workflow.py` and `advanced_orchestration.py` files show the intended multi-agent architecture but require Agent Framework enhancements to support SAP AI Core's query parameter requirements.

## Examples

### Example 1: SAP Data Analysis Workflow
The system analyzes SAP sales data with multiple specialized agents working together.

### Example 2: SAP System Integration
Demonstrates how agents collaborate to integrate external systems with SAP.

### Example 3: Compliance Check
Shows security and compliance validation across SAP operations.

## Key Features

- **Automatic Token Refresh**: Tokens are refreshed automatically before expiration
- **Thread-Safe Operations**: Safe for concurrent agent execution
- **Error Recovery**: Robust error handling and retry mechanisms
- **Extensible Architecture**: Easy to add new specialized agents
- **Production-Ready**: Follows SAP AI Core best practices

## Architecture Diagram

```
┌─────────────────────────────────────────────────────┐
│                  User Request                        │
└───────────────────┬─────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────┐
│              Coordinator Agent                       │
│  (Orchestrates workflow & manages collaboration)     │
└───────┬─────────────┬─────────────┬─────────────────┘
        │             │             │
        ▼             ▼             ▼
  ┌──────────┐  ┌──────────┐  ┌──────────┐
  │Data      │  │Integration│  │Security  │
  │Analyst   │  │Specialist│  │Auditor   │
  └────┬─────┘  └────┬─────┘  └────┬─────┘
       │             │             │
       └─────────────┴─────────────┘
                     │
                     ▼
          ┌──────────────────────┐
          │   SAPTokenManager    │
          │ (Centralized Auth)   │
          └──────────┬───────────┘
                     │
                     ▼
          ┌──────────────────────┐
          │   SAP AI Core API    │
          └──────────────────────┘
```

## Troubleshooting

### Authentication Issues
- Verify credentials in `.env` file
- Check token expiration and refresh logs
- Ensure OAuth2 endpoint is accessible

### Agent Communication
- Review agent instructions for clarity
- Check max rounds configuration
- Monitor token usage and rate limits

## Additional Resources

- [SAP AI Core Documentation](https://help.sap.com/docs/ai-core)
- [Agent Framework Documentation](../../python/README.md)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
