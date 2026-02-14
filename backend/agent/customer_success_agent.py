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

    async def run(self, message: str, context: Dict[str, Any]) -> str:
        """
        Runs the agent loop:
        1. Formats system prompt with context.
        2. Calls OpenAI API with tools.
        3. Executes tools if requested.
        4. returns final response.
        """
        customer_id = context.get("customer_id", "unknown")
        conversation_id = context.get("conversation_id", "unknown")
        channel = context.get("channel", "unknown")

        system_instruction = SYSTEM_PROMPT.format(
            channel=channel,
            customer_id=customer_id,
            conversation_id=conversation_id
        )

        messages = [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": message}
        ]

        # TODO: Inject history here if not handled by get_customer_history tool implicitly
        # (Though the tool is better for "retrieving" history, passing recent history 
        # in `messages` is better for immediate context).
        # We will assume the `message_processor` passes a few recent messages in `context` or we prepend them.
        
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
                        
                        # Inject IDs into args if missing and required by the tool Pydantic model
                        if "customer_id" in function_args and not function_args["customer_id"]:
                             function_args["customer_id"] = customer_id
                        if "conversation_id" in function_args and not function_args["conversation_id"]:
                             function_args["conversation_id"] = conversation_id
                        
                        # We need to construct the input object expected by validation, 
                        # but our wrappers in available_tools accept the raw dict or pydantic model?
                        # In tools.py, we defined: async def search_knowledge_base(args: KnowledgeSearchInput)
                        # So we need to instantiate the model.
                        
                        # Quick helper to bind args to the Pydantic model
                        # For MVP simplicity, let's assume `function_to_call` can handle the dict 
                        # OR we explicitly handle it here. 
                        # Let's adjust this logic to pass the Pydantic model.
                        
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
                return final_response.choices[0].message.content
            
            return assistant_message.content

        except Exception as e:
            logger.error(f"Agent execution error: {e}", exc_info=True)
            return "I apologize, but I'm encountering a technical issue processing your request. Please try again later."
