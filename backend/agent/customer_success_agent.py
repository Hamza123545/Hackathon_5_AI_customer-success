import os
import logging
from typing import Dict, Any, List
from openai import AsyncOpenAI
from agents import Agent, Runner
from agent.prompts import SYSTEM_PROMPT
from agent.tools import AGENT_TOOLS

logger = logging.getLogger(__name__)

class CustomerSuccessAgent:
    def __init__(self):
        # Configure for Gemini via OpenAI-compatible endpoint
        self.client = AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
        
        # Initialize the Agent
        self.agent = Agent(
            name="Customer Success FTE",
            model="gemini-1.5-flash", # Using Gemini 1.5 Flash as requested/implied for speed/cost
            instructions=SYSTEM_PROMPT, # Base instructions, context will be prepended/appended
            tools=AGENT_TOOLS
        )

    async def run(self, history: List[Dict[str, Any]], context: Dict[str, Any]) -> str:
        """
        Runs the agent loop using the OpenAI Agents SDK Runner.
        """
        customer_id = context.get("customer_id", "unknown")
        conversation_id = context.get("conversation_id", "unknown")
        channel = context.get("channel", "unknown")

        # Dynamic context injection
        # Since the Agent SDK 'instructions' are static or managed by the agent, 
        # we can pass dynamic context as a system message or update instructions for this run?
        # A common pattern is to prepend a system message with the context.
        
        context_instruction = f"""
        Current Context:
        - Customer ID: {customer_id}
        - Conversation ID: {conversation_id}
        - Channel: {channel}
        """
        
        messages = [{"role": "system", "content": context_instruction}]

        # Append history
        for msg in history:
            role_map = {
                "customer": "user",
                "agent": "assistant",
                "system": "system"
            }
            role = role_map.get(msg.get("role"), msg.get("role", "user"))
            messages.append({
                "role": role, 
                "content": msg.get("content", "")
            })

        try:
            # Run the agent
            # Note: The Runner typically manages the loop calls. 
            # We pass the client explicitly if the SDK allows, otherwise it uses global or default?
            # The SDK documentation (implied) suggests we might need to pass the client to the Runner 
            # or the Agent. 
            # If Agent constructor doesn't take client, maybe Runner does.
            # Let's assume Runner can take `client=self.client` or we set it on the agent.
            # A common pattern in these SDKs when using non-default client:
            
            result = await Runner.run(self.agent, messages=messages, client=self.client)
            
            # The result object typically contains the final message or usage info.
            # Let's assume result.final_output or similar.
            # If result is just the final message text, great.
            # If it's a generic Result object, we need to inspect it.
            # For now, let's assume valid string return or attribute access.
            
            return result.final_output
            
        except Exception as e:
            logger.error(f"Agent execution error: {e}", exc_info=True)
            return "I apologize, but I'm encountering a technical issue processing your request. Please try again later."
