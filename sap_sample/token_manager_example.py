"""
Example using SAPTokenManager for authenticated requests, chat, and agent integration
"""

import os
import requests  # Still needed for listing deployments
from dotenv import load_dotenv
from openai import OpenAI
from token_manager import SAPTokenManager

# Load environment variables
load_dotenv()

def chat_completion_example(token_manager: SAPTokenManager):
    """Example of using SAP AI Core for chat completions with OpenAI package"""
    print("\n" + "="*50)
    print("SAP AI Core Chat Completion Example")
    print("="*50)
    
    base_url = os.getenv('AICORE_BASE_URL')
    deployment_id = os.getenv('AICORE_DEPLOYMENT_ID')
    resource_group = os.getenv('AICORE_RESOURCE_GROUP')
    
    if not deployment_id:
        print("⚠ Skipping chat example - AICORE_DEPLOYMENT_ID not set")
        return
    
    try:
        # Create OpenAI client configured for SAP AI Core
        # For Azure OpenAI models, use the deployment URL with api-version parameter
        api_version = "2024-02-01"
        client = OpenAI(
            base_url=f"{base_url}/v2/inference/deployments/{deployment_id}",
            api_key=token_manager.get_token(),
            default_headers={"AI-Resource-Group": resource_group}
        )
        
        print("\nSending chat request to SAP AI Core...")
        
        # Use the OpenAI client to make the chat completion request
        response = client.chat.completions.create(
            model="gpt-4o",  # Model name is required but ignored by SAP AI Core
            messages=[
                {
                    "role": "user",
                    "content": "Hello! Can you help me understand SAP AI Core?"
                }
            ],
            max_tokens=100,
            temperature=0.7,
            extra_query={"api-version": api_version}
        )
        
        print(f"✓ Response received")
        message = response.choices[0].message.content
        print(f"\nAssistant: {message}")
            
    except Exception as e:
        print(f"✗ Error: {e}")


def agent_example(token_manager: SAPTokenManager):
    """Example of using SAP AI Core as an agent with tools using OpenAI package"""
    print("\n" + "="*50)
    print("SAP AI Core Agent Example")
    print("="*50)
    
    base_url = os.getenv('AICORE_BASE_URL')
    deployment_id = os.getenv('AICORE_DEPLOYMENT_ID')
    resource_group = os.getenv('AICORE_RESOURCE_GROUP')
    
    if not deployment_id:
        print("⚠ Skipping agent example - AICORE_DEPLOYMENT_ID not set")
        return
    
    try:
        # Create OpenAI client configured for SAP AI Core
        api_version = "2024-02-01"
        client = OpenAI(
            base_url=f"{base_url}/v2/inference/deployments/{deployment_id}",
            api_key=token_manager.get_token(),
            default_headers={"AI-Resource-Group": resource_group}
        )
        
        print("\nSending agent request with tools to SAP AI Core...")
        
        # Use the OpenAI client with tool calling
        response = client.chat.completions.create(
            model="gpt-4o",  # Model name is required but ignored by SAP AI Core
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful AI assistant with access to tools."
                },
                {
                    "role": "user",
                    "content": "What's the weather like today?"
                }
            ],
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "get_weather",
                        "description": "Get the current weather for a location",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "location": {
                                    "type": "string",
                                    "description": "City name"
                                }
                            },
                            "required": ["location"]
                        }
                    }
                }
            ],
            tool_choice="auto",
            max_tokens=150,
            extra_query={"api-version": api_version}
        )
        
        print(f"✓ Response received")
        
        choice = response.choices[0]
        message = choice.message
        
        # Check if agent wants to call a tool
        if message.tool_calls:
            print("\n🔧 Agent requested tool calls:")
            for tool_call in message.tool_calls:
                print(f"  - {tool_call.function.name}")
                print(f"    Arguments: {tool_call.function.arguments}")
        else:
            print(f"\nAssistant: {message.content if message.content else 'No content'}")
            
    except Exception as e:
        print(f"✗ Error: {e}")


def list_deployments_example(token_manager: SAPTokenManager):
    """Example of listing available deployments"""
    print("\n" + "="*50)
    print("List SAP AI Core Deployments")
    print("="*50)
    
    base_url = os.getenv('AICORE_BASE_URL')
    headers = token_manager.get_auth_headers()
    
    try:
        print("\nFetching deployments...")
        response = requests.get(
            f"{base_url}/v2/lm/deployments",
            headers=headers,
            timeout=30
        )
        
        response.raise_for_status()
        result = response.json()
        
        print(f"✓ Deployments retrieved (status: {response.status_code})")
        
        if 'resources' in result:
            deployments = result['resources']
            print(f"\nFound {len(deployments)} deployment(s):")
            for deployment in deployments:  # Show all deployments
                print(f"\n  - ID: {deployment.get('id')}")
                print(f"    Status: {deployment.get('status')}")
                print(f"    Scenario ID: {deployment.get('scenarioId', 'N/A')}")
                print(f"    Configuration ID: {deployment.get('configurationId', 'N/A')}")
                print(f"    Configuration Name: {deployment.get('configurationName', 'N/A')}")
                print(f"    Deployment URL: {deployment.get('deploymentUrl', 'N/A')}")
                print(f"    Created At: {deployment.get('createdAt', 'N/A')}")
                print(f"    Modified At: {deployment.get('modifiedAt', 'N/A')}")
                print(f"    Submission Time: {deployment.get('submissionTime', 'N/A')}")
                print(f"    Start Time: {deployment.get('startTime', 'N/A')}")
                if deployment.get('details'):
                    print(f"    Details: {deployment.get('details')}")
                if deployment.get('targetStatus'):
                    print(f"    Target Status: {deployment.get('targetStatus')}")
                if deployment.get('latestRunningConfigurationId'):
                    print(f"    Latest Running Config: {deployment.get('latestRunningConfigurationId')}")
        else:
            print(f"\nResponse: {result}")
            
    except Exception as e:
        print(f"✗ Error: {e}")


def main():
    """Example of using the token manager with various SAP AI Core features"""
    print("SAP AI Core Token Manager - Complete Example\n" + "="*50)
    
    # Initialize token manager
    token_manager = SAPTokenManager()
    
    # 1. Test basic token retrieval
    print("\n1. Token Retrieval Test")
    headers = token_manager.get_auth_headers()
    print(f"✓ Token obtained: {headers['Authorization'][:30]}...")
    
    # 2. List available deployments
    list_deployments_example(token_manager)
    
    # 3. Chat completion example
    chat_completion_example(token_manager)
    
    # 4. Agent with tools example
    agent_example(token_manager)
    
    # 5. Test token reuse
    print("\n" + "="*50)
    print("Token Reuse Test")
    print("="*50)
    print("\nMaking another request - token will be reused if still valid")
    headers = token_manager.get_auth_headers()
    print(f"✓ Using token: {headers['Authorization'][:30]}...")
    
    # 6. Force refresh
    print("\n" + "="*50)
    print("Force Token Refresh")
    print("="*50)
    token_manager.force_refresh()
    headers = token_manager.get_auth_headers()
    print(f"✓ New token: {headers['Authorization'][:30]}...")
    
    print("\n" + "="*50)
    print("✓ All examples completed successfully!")
    print("="*50)

if __name__ == "__main__":
    main()