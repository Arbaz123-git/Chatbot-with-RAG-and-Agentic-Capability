from groq import Groq
from typing import List, Dict
from app.config import settings
from app.agent.tools import web_search_tool, calculator_tool
from app.utils.logger import step_logger
import re

class AgentService:
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = settings.AGENT_MODEL
        self.max_iterations = 3
    
    def _create_system_prompt(self) -> str:
        return """You have 2 tools:
- web_search: Search the web for current info
- calculator: Do math calculations

To use a tool:
Action: tool_name
Action Input: your input

When done:
Final Answer: your response"""
    
    def _parse_action(self, text: str) -> tuple:
        action_match = re.search(r"Action:\s*(\w+)", text, re.IGNORECASE)
        input_match = re.search(r"Action Input:\s*(.+?)(?:\n|$)", text, re.IGNORECASE | re.DOTALL)
        
        if action_match and input_match:
            return action_match.group(1).strip(), input_match.group(1).strip()
        return None, None
    
    def _parse_final_answer(self, text: str) -> str:
        match = re.search(r"Final Answer:\s*(.+)", text, re.IGNORECASE | re.DOTALL)
        return match.group(1).strip() if match else None
    
    def _execute_tool(self, action: str, action_input: str) -> str:
        step_logger.step(f"Executing tool: {action}", "AGENT")
        step_logger.info(f"Tool input: {action_input[:100]}...", "AGENT")
        
        if action.lower() == "web_search":
            result = web_search_tool.search(action_input)
            step_logger.step(f"Web search completed, result length: {len(result)} chars", "AGENT")
            return result
        elif action.lower() == "calculator":
            result = calculator_tool.calculate(action_input)
            step_logger.step(f"Calculator result: {result}", "AGENT")
            return result
        return f"Unknown tool: {action}"
    
    def process_with_tools(self, messages: List[Dict]) -> str:
        step_logger.step("Starting agent processing (non-streaming)", "AGENT")
        
        try:
            user_message = messages[-1]["content"] if messages else ""
            step_logger.info(f"User message: {user_message[:100]}...", "AGENT")
            
            conversation = [
                {"role": "system", "content": self._create_system_prompt()},
                {"role": "user", "content": user_message}
            ]
            
            for iteration in range(self.max_iterations):
                step_logger.step(f"Agent iteration {iteration + 1}/{self.max_iterations}", "AGENT")
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=conversation,
                    max_tokens=512,
                    temperature=0.0
                )
                
                response_text = response.choices[0].message.content
                step_logger.info(f"LLM response: {response_text[:100]}...", "AGENT")
                
                final_answer = self._parse_final_answer(response_text)
                if final_answer:
                    step_logger.step("Final answer found", "AGENT")
                    return final_answer
                
                action, action_input = self._parse_action(response_text)
                
                if action and action_input:
                    step_logger.step(f"Tool detected: {action}", "AGENT")
                    tool_result = self._execute_tool(action, action_input)
                    if len(tool_result) > 1000:
                        tool_result = tool_result[:1000] + "..."
                    
                    conversation.append({"role": "assistant", "content": response_text})
                    conversation.append({"role": "user", "content": f"Observation: {tool_result}"})
                else:
                    step_logger.step("No tool action, returning response", "AGENT")
                    return response_text
            
            step_logger.step("Max iterations reached", "AGENT")
            return "Could not complete the task."
            
        except Exception as e:
            step_logger.error(f"Error: {str(e)}", "AGENT")
            return f"Error: {str(e)}"
    
    async def process_with_tools_streaming(self, messages: List[Dict]):
        step_logger.step("Starting agent processing (streaming)", "AGENT")
        
        try:
            user_message = messages[-1]["content"] if messages else ""
            step_logger.info(f"User message: {user_message[:100]}...", "AGENT")
            
            conversation = [
                {"role": "system", "content": self._create_system_prompt()},
                {"role": "user", "content": user_message}
            ]
            
            for iteration in range(self.max_iterations):
                step_logger.step(f"Agent iteration {iteration + 1}/{self.max_iterations}", "AGENT")
                
                response_text = ""
                stream = self.client.chat.completions.create(
                    model=self.model,
                    messages=conversation,
                    max_tokens=512,
                    temperature=0.0,
                    stream=True
                )
                
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        response_text += chunk.choices[0].delta.content
                
                step_logger.info(f"LLM response received: {response_text[:100]}...", "AGENT")
                
                final_answer = self._parse_final_answer(response_text)
                if final_answer:
                    step_logger.step("Final answer found, sending to user", "AGENT")
                    step_logger.result(final_answer)
                    yield final_answer
                    return

                action, action_input = self._parse_action(response_text)

                if action and action_input:
                    step_logger.step(f"Tool detected: {action}", "AGENT")
                    yield f"[Using {action}] "
                    tool_result = self._execute_tool(action, action_input)
                    if len(tool_result) > 1000:
                        tool_result = tool_result[:1000] + "..."
                    
                    conversation.append({"role": "assistant", "content": response_text})
                    conversation.append({"role": "user", "content": f"Observation: {tool_result}"})
                else:
                    step_logger.step("No tool action, returning response", "AGENT")
                    yield response_text
                    return
            
            step_logger.step("Max iterations reached", "AGENT")
            yield "Could not complete."
            
        except Exception as e:
            step_logger.error(f"Error: {str(e)}", "AGENT")
            yield f"\nError: {str(e)}"

agent_service = AgentService()