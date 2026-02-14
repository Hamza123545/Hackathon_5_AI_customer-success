import os
import json
import logging
from typing import Dict, Any, List
from openai import AsyncOpenAI
from agent.prompts import SYSTEM_PROMPT
from agent.tools import TOOL_DEFINITIONS, AVAILABLE_TOOLS

logger = logging.getLogger(__name__)

class CustomerSuccessAgent:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4-turbo-preview" # Or gpt-3.5-turbo if cost is a concern

    async def run(self, history: List[Dict[str, Any]], context: Dict[str, Any]) -> Any:
        """
        Runs the agent loop:
        1. Formats system prompt with context.
        2. Prepares message history (mapping DB roles to OpenAI roles).
        3. Calls OpenAI API with tools.
        4. Executes tools if requested.
        5. Returns final response.
        """
        customer_id = context.get("customer_id", "unknown")
        conversation_id = context.get("conversation_id", "unknown")
        channel = context.get("channel", "unknown")

        system_instruction = SYSTEM_PROMPT.format(
            channel=channel,
            customer_id=customer_id,
            conversation_id=conversation_id
        )

        # 1. Start with system prompt
        messages = [{"role": "system", "content": system_instruction}]

        # 2. Append history
        # Expecting history items to have keys: 'role', 'content'
        # DB roles: 'customer', 'agent', 'system' -> OpenAI: 'user', 'assistant', 'system'
        for msg in history:
            role_map = {
                "customer": "user",
                "agent": "assistant",
                "system": "system"
            }
            # Default to 'user' if unknown, or keep as is if already correct
            role = role_map.get(msg.get("role"), msg.get("role", "user"))
            
            messages.append({
                "role": role, 
                "content": msg.get("content", "")
            })

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=TOOL_DEFINITIONS,
                tool_choice="auto"
            )

            assistant_message = response.choices[0].message
            
            # Handle tool calls
            if assistant_message.tool_calls:
                messages.append(assistant_message) # Add the assistant's request to history
                
                for tool_call in assistant_message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    logger.info(f"Agent calling tool: {function_name} with {function_args}")
                    
                    if function_name in AVAILABLE_TOOLS:
                        function_to_call = AVAILABLE_TOOLS[function_name]
                        
                        # Inject IDs into args if missing
                        if "customer_id" in function_args and not function_args["customer_id"]:
                             function_args["customer_id"] = customer_id
                        if "conversation_id" in function_args and not function_args["conversation_id"]:
                             function_args["conversation_id"] = conversation_id
                        
                        from agent.tools import KnowledgeSearchInput, TicketInput, CustomerHistoryInput, EscalationInput
                        
                        tool_output = ""
                        try:
                            if function_name == "search_knowledge_base":
                                input_data = KnowledgeSearchInput(**function_args)
                                tool_output = await function_to_call(input_data)
                            elif function_name == "create_ticket":
                                input_data = TicketInput(**function_args)
                                tool_output = await function_to_call(input_data)
                            elif function_name == "get_customer_history":
                                input_data = CustomerHistoryInput(**function_args)
                                tool_output = await function_to_call(input_data)
                            elif function_name == "escalate_to_human":
                                input_data = EscalationInput(**function_args)
                                tool_output = await function_to_call(input_data)
                        except Exception as e:
                            tool_output = json.dumps({"error": f"Tool execution error: {str(e)}"})
                        
                        messages.append({
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": tool_output,
                        })
                
                # Get final response after tool outputs
                final_response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages
                )
                
                # Return object with output and potential escalation status
                # For now, just string content, but caller might need more.
                # The message processor stores "result.output".
                # If we need escalation flag, we might parse it or rely on the tool side effect.
                # The 'escalate_to_human' tool updates the ticket status.
                
                return final_response.choices[0].message.content
            
            return assistant_message.content

        except Exception as e:
            logger.error(f"Agent execution error: {e}", exc_info=True)
            return "I apologize, but I'm encountering a technical issue processing your request. Please try again later."
