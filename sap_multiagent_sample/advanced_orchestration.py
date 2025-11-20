# Copyright (c) Microsoft. All rights reserved.
"""
SAP Advanced Multi-Agent Orchestration

Demonstrates advanced orchestration patterns:
- Parallel agent execution for concurrent analysis
- Conditional routing based on agent responses
- Error handling and recovery strategies
- Token refresh during long-running workflows
"""

import asyncio
import os
from typing import List
from dotenv import load_dotenv

from agent_framework import (
    AgentRunUpdateEvent,
    GroupChatBuilder,
    SequentialBuilder,
    WorkflowOutputEvent
)
from agent_framework.openai import OpenAIChatClient
from sap_token_manager import get_token_manager

# Load environment variables
load_dotenv()


def create_sap_client() -> OpenAIChatClient:
    """Create SAP AI Core client with authentication"""
    token_manager = get_token_manager()
    base_url = os.getenv('AICORE_BASE_URL')
    deployment_id = os.getenv('AICORE_DEPLOYMENT_ID')
    resource_group = os.getenv('AICORE_RESOURCE_GROUP', 'default')
    
    return OpenAIChatClient(
        model_id="gpt-4o",
        api_key=token_manager.get_token(),
        base_url=f"{base_url}/v2/inference/deployments/{deployment_id}",
        default_headers={"AI-Resource-Group": resource_group}
    )


async def parallel_analysis_workflow():
    """
    Demonstrate parallel agent execution for concurrent analysis.
    
    Multiple agents analyze different aspects of SAP data simultaneously,
    then results are synthesized.
    """
    print("=" * 80)
    print("Parallel Analysis Workflow")
    print("=" * 80)
    print("\nScenario: Concurrent analysis of SAP system performance\n")
    
    client = create_sap_client()
    
    # Create specialized analysis agents
    performance_analyzer = client.create_agent(
        name="Performance_Analyzer",
        instructions="""Analyze SAP system performance metrics: response times, 
        throughput, resource utilization. Identify bottlenecks and optimization opportunities.""",
        description="SAP performance analysis expert"
    )
    
    security_analyzer = client.create_agent(
        name="Security_Analyzer",
        instructions="""Analyze SAP security posture: access controls, audit logs, 
        vulnerability assessment. Identify security gaps and recommendations.""",
        description="SAP security analysis expert"
    )
    
    cost_analyzer = client.create_agent(
        name="Cost_Analyzer",
        instructions="""Analyze SAP operational costs: licensing, infrastructure, 
        maintenance costs. Identify cost optimization opportunities.""",
        description="SAP cost analysis expert"
    )
    
    synthesizer = client.create_agent(
        name="Report_Synthesizer",
        instructions="""Synthesize findings from multiple analysts into a cohesive 
        executive summary. Prioritize recommendations by impact and effort.""",
        description="Synthesizes multi-agent analysis"
    )
    
    # First, run parallel analysis
    print("Phase 1: Parallel Analysis")
    print("-" * 80)
    
    analysis_task = """Analyze our SAP S/4HANA production system based on last month's 
    operational data. Focus on your area of expertise."""
    
    # Collect results from parallel execution
    results = []
    
    async def run_agent_analysis(agent, agent_name: str):
        """Run single agent analysis and collect results"""
        print(f"\n[{agent_name}] Starting analysis...")
        response_parts = []
        
        async for response in agent.run_stream(analysis_task):
            if hasattr(response, 'text') and response.text:
                response_parts.append(response.text)
        
        full_response = ''.join(response_parts)
        results.append(f"{agent_name} findings:\n{full_response}")
        print(f"[{agent_name}] ✓ Analysis complete")
        return full_response
    
    # Run agents in parallel
    await asyncio.gather(
        run_agent_analysis(performance_analyzer, "Performance_Analyzer"),
        run_agent_analysis(security_analyzer, "Security_Analyzer"),
        run_agent_analysis(cost_analyzer, "Cost_Analyzer")
    )
    
    # Phase 2: Synthesize results
    print("\n\nPhase 2: Synthesis")
    print("-" * 80)
    
    synthesis_task = f"""Based on the following expert analyses, create a prioritized 
    executive summary with actionable recommendations:

    {chr(10).join(results)}
    """
    
    print("\n[Report_Synthesizer] Synthesizing findings...")
    async for response in synthesizer.run_stream(synthesis_task):
        if hasattr(response, 'text') and response.text:
            print(response.text, end="", flush=True)
    
    print("\n\n" + "=" * 80)
    print("✓ Parallel analysis workflow completed")
    print("=" * 80)


async def conditional_routing_workflow():
    """
    Demonstrate conditional agent routing based on context.
    
    Route requests to appropriate specialists based on the nature
    of the SAP issue or question.
    """
    print("\n\n" + "=" * 80)
    print("Conditional Routing Workflow")
    print("=" * 80)
    print("\nScenario: Intelligent routing of SAP support requests\n")
    
    client = create_sap_client()
    
    # Create triage agent
    triage_agent = client.create_agent(
        name="Support_Triage",
        instructions="""You are a triage agent for SAP support requests. Analyze the request 
        and classify it as: TECHNICAL (system issues), SECURITY (access/compliance), 
        FUNCTIONAL (business process), or INTEGRATION (system connectivity). 
        Start your response with exactly one of these classifications in brackets.""",
        description="Classifies and routes SAP support requests"
    )
    
    # Create specialist agents
    technical_specialist = client.create_agent(
        name="Technical_Specialist",
        instructions="""Handle technical SAP issues: system errors, performance problems, 
        configuration issues. Provide detailed troubleshooting steps.""",
        description="SAP technical support specialist"
    )
    
    security_specialist = client.create_agent(
        name="Security_Specialist",
        instructions="""Handle SAP security issues: access problems, authentication, 
        authorization, compliance. Provide security-focused solutions.""",
        description="SAP security specialist"
    )
    
    functional_specialist = client.create_agent(
        name="Functional_Specialist",
        instructions="""Handle SAP functional issues: business process questions, 
        workflow configuration, master data. Provide business-focused guidance.""",
        description="SAP functional consultant"
    )
    
    integration_specialist = client.create_agent(
        name="Integration_Specialist",
        instructions="""Handle SAP integration issues: API connectivity, data exchange, 
        middleware problems. Provide integration troubleshooting.""",
        description="SAP integration specialist"
    )
    
    # Test cases for routing
    test_requests = [
        "Our SAP system is running slow and users are experiencing timeouts",
        "A user cannot access the Purchase Order approval workflow",
        "The integration between SAP and Salesforce stopped syncing data"
    ]
    
    for i, request in enumerate(test_requests, 1):
        print(f"\nRequest {i}: {request}")
        print("-" * 80)
        
        # Phase 1: Triage
        print("\n[Support_Triage] Analyzing request...")
        classification = []
        async for response in triage_agent.run_stream(request):
            if hasattr(response, 'text') and response.text:
                classification.append(response.text)
                print(response.text, end="", flush=True)
        
        triage_result = ''.join(classification)
        
        # Phase 2: Route to specialist
        print("\n\n[Routing] Directing to appropriate specialist...")
        
        # Simple classification logic
        if "TECHNICAL" in triage_result.upper():
            specialist = technical_specialist
        elif "SECURITY" in triage_result.upper():
            specialist = security_specialist
        elif "INTEGRATION" in triage_result.upper():
            specialist = integration_specialist
        else:
            specialist = functional_specialist
        
        print(f"[{specialist.name}] Handling request...\n")
        async for response in specialist.run_stream(request):
            if hasattr(response, 'text') and response.text:
                print(response.text, end="", flush=True)
        
        print("\n" + "=" * 80)
    
    print("\n✓ Conditional routing workflow completed")


async def error_recovery_workflow():
    """
    Demonstrate error handling and recovery in multi-agent workflows.
    
    Shows how to handle token expiration, API errors, and graceful degradation.
    """
    print("\n\n" + "=" * 80)
    print("Error Recovery Workflow")
    print("=" * 80)
    print("\nScenario: Robust error handling in long-running workflows\n")
    
    token_manager = get_token_manager()
    
    # Simulate token refresh monitoring
    print(f"Token status: Valid={token_manager.is_token_valid()}")
    print(f"Token expires at: {token_manager.expires_at.strftime('%Y-%m-%d %H:%M:%S') if token_manager.expires_at else 'Unknown'}")
    
    try:
        client = create_sap_client()
        
        agent = client.create_agent(
            name="Resilient_Agent",
            instructions="You are a resilient SAP assistant that handles errors gracefully.",
            description="Error-resilient SAP agent"
        )
        
        print("\n[Resilient_Agent] Executing long-running task with error monitoring...")
        
        # Simulate a task that might trigger token refresh
        task = "Provide a comprehensive guide to SAP S/4HANA migration best practices."
        
        async for response in agent.run_stream(task):
            if hasattr(response, 'text') and response.text:
                print(response.text, end="", flush=True)
                
                # Check token status periodically
                if not token_manager.is_token_valid():
                    print("\n\n⚠ Token refresh triggered during execution...")
        
        print("\n\n✓ Task completed with error monitoring")
        print(f"Final token status: Valid={token_manager.is_token_valid()}")
        
    except Exception as e:
        print(f"\n✗ Error occurred: {e}")
        print("Implementing recovery strategy...")
        
        # Recovery: Force token refresh and retry
        token_manager.force_refresh()
        print("✓ Token refreshed, ready for retry")
    
    print("\n" + "=" * 80)
    print("✓ Error recovery workflow completed")
    print("=" * 80)


async def main():
    """Run all advanced orchestration examples"""
    try:
        await parallel_analysis_workflow()
        await conditional_routing_workflow()
        await error_recovery_workflow()
        
    except Exception as e:
        print(f"\n✗ Workflow error: {e}")
        raise


if __name__ == "__main__":
    print("\n🚀 Starting SAP Advanced Orchestration Examples\n")
    asyncio.run(main())
    print("\n✅ All advanced workflows completed!\n")
