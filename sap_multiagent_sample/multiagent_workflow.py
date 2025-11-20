# Copyright (c) Microsoft. All rights reserved.
"""
SAP Multi-Agent Workflow Example

Demonstrates a coordinated multi-agent system for SAP AI Core with:
- Specialized agents for different SAP domains
- Centralized authentication using SAPTokenManager
- Dynamic agent selection based on task context
- Production-ready error handling
"""

import asyncio
import os
from dotenv import load_dotenv
from openai import AsyncOpenAI

from sap_token_manager import get_token_manager

# Load environment variables
load_dotenv()


def create_sap_openai_client(token_manager) -> AsyncOpenAI:
    """
    Create an OpenAI client configured for SAP AI Core.
    
    Args:
        token_manager: SAPTokenManager instance for authentication
        
    Returns:
        AsyncOpenAI: Configured client for SAP AI Core
    """
    base_url = os.getenv('AICORE_BASE_URL')
    deployment_id = os.getenv('AICORE_DEPLOYMENT_ID')
    resource_group = os.getenv('AICORE_RESOURCE_GROUP', 'default')
    api_version = "2024-02-01"
    
    if not all([base_url, deployment_id]):
        raise ValueError("Missing required environment variables: AICORE_BASE_URL, AICORE_DEPLOYMENT_ID")
    
    # Create AsyncOpenAI client configured for SAP AI Core
    return AsyncOpenAI(
        base_url=f"{base_url}/v2/inference/deployments/{deployment_id}",
        api_key=token_manager.get_token(),
        default_headers={"AI-Resource-Group": resource_group},
        default_query={"api-version": api_version}
    )


async def run_sap_data_analysis_workflow():
    """
    Demonstrate multi-agent workflow for SAP data analysis using direct conversation.
    
    Scenario: Analyzing SAP sales data with multiple specialized agents
    collaborating to provide comprehensive insights.
    """
    print("=" * 80)
    print("SAP Multi-Agent Data Analysis Workflow")
    print("=" * 80)
    
    # Get shared token manager (singleton)
    token_manager = get_token_manager()
    print(f"\nToken manager initialized (Token valid: {token_manager.is_token_valid()})")
    
    # Create SAP AI Core client
    client = create_sap_openai_client(token_manager)
    print("SAP AI Core client configured\n")
    
    # Define agent roles and their expertise
    agents = {
        "Data_Analyst": {
            "role": "SAP Data Analyst",
            "instructions": """You are an expert SAP data analyst specializing in sales and financial data.
Your role: Analyze SAP sales data patterns, identify KPIs, provide data-driven insights.
Keep responses concise and data-focused."""
        },
        "Integration_Specialist": {
            "role": "SAP Integration Specialist", 
            "instructions": """You are an SAP integration specialist focused on system connectivity.
Your role: Advise on SAP API integrations, data flows, and best practices.
Keep responses technical and integration-focused."""
        },
        "Security_Auditor": {
            "role": "SAP Security Auditor",
            "instructions": """You are an SAP security and compliance auditor.
Your role: Review security implications, ensure compliance, identify risks.
Keep responses security and compliance-focused."""
        }
    }
    
    # Complex SAP scenario requiring multiple expert perspectives
    task = """I need to analyze our Q4 sales data from SAP S/4HANA and create a dashboard 
that integrates with our external CRM system. The dashboard will be accessed by sales managers 
across different regions. What approach would you recommend, considering data analysis, 
integration requirements, and security compliance?"""
    
    print(f"Task: {task}\n")
    print("-" * 80)
    
    # Simulate multi-agent collaboration by calling each expert in sequence
    conversation_history = []
    
    for agent_name, agent_info in agents.items():
        print(f"\n{'=' * 80}")
        print(f"Agent: {agent_info['role']}")
        print(f"{'=' * 80}\n")
        
        # Build context from previous responses
        context = "\n\n".join([f"{msg['agent']}: {msg['response']}" for msg in conversation_history])
        
        # Create prompt with agent role and conversation context
        messages = [
            {
                "role": "system",
                "content": agent_info['instructions']
            },
            {
                "role": "user",
                "content": f"""Given this request: {task}

{"Previous expert responses:" + context if context else ""}

Based on your expertise as a {agent_info['role']}, provide your analysis and recommendations. 
Be specific and actionable. If previous experts have provided input, build upon their insights."""
            }
        ]
        
        # Get response from SAP AI Core
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=300,
            temperature=0.7,
            stream=False
        )
        
        agent_response = response.choices[0].message.content
        print(agent_response)
        
        # Add to conversation history
        conversation_history.append({
            "agent": agent_info['role'],
            "response": agent_response
        })
    
    print("\n" + "=" * 80)
    print("✓ Workflow completed successfully")
    print("=" * 80)


async def run_sap_integration_workflow():
    """
    Demonstrate sequential workflow for SAP system integration planning.
    
    Scenario: Planning a new integration between SAP and external systems
    with security validation.
    """
    print("\n\n" + "=" * 80)
    print("SAP Integration Planning Workflow")
    print("=" * 80)
    
    # Reuse the shared token manager
    token_manager = get_token_manager()
    print(f"\nReusing token manager (Token valid: {token_manager.is_token_valid()})")
    
    client = create_sap_openai_client(token_manager)
    
    # Define sequential workflow: Architect designs, then Security reviews
    agents_sequence = [
        {
            "name": "Integration Architect",
            "instructions": """You are an SAP integration architect. Design integration solutions 
considering: API selection, data mapping, error handling, and scalability. 
Provide technical architecture recommendations with specific implementation details."""
        },
        {
            "name": "Security Reviewer",
            "instructions": """You are a security reviewer for SAP integrations. Review the integration 
design provided by the architect for: authentication methods, data encryption, access controls, 
and compliance. Identify security risks and provide mitigation strategies."""
        }
    ]
    
    task = """Design an integration between SAP S/4HANA and Salesforce to sync customer 
master data in real-time. Include architecture and security assessment."""
    
    print(f"\nTask: {task}\n")
    print("-" * 80)
    
    previous_output = None
    
    for agent in agents_sequence:
        print(f"\n{'=' * 80}")
        print(f"Agent: {agent['name']}")
        print(f"{'=' * 80}\n")
        
        # Build messages with previous agent's output as context
        messages = [
            {
                "role": "system",
                "content": agent['instructions']
            },
            {
                "role": "user",
                "content": task if not previous_output else f"""{task}

Previous expert provided:
{previous_output}

Based on this, provide your analysis and recommendations from your perspective as {agent['name']}."""
            }
        ]
        
        # Get response from SAP AI Core
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=400,
            temperature=0.7,
            stream=False
        )
        
        agent_response = response.choices[0].message.content
        print(agent_response)
        
        previous_output = agent_response
    
    print("\n" + "=" * 80)
    print("✓ Integration workflow completed")
    print("=" * 80)


async def main():
    """Run all SAP multi-agent workflow examples"""
    try:
        # Run data analysis workflow
        await run_sap_data_analysis_workflow()
        
        # Run integration planning workflow
        await run_sap_integration_workflow()
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        raise


if __name__ == "__main__":
    print("\nStarting SAP Multi-Agent Workflows\n")
    asyncio.run(main())
    print("\nAll workflows completed successfully!\n")
