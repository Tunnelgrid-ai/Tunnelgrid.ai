"""
OpenAI Basic API Service

This module provides a basic interface to OpenAI's Responses API with web search capabilities.
It handles system and user prompts, enables web search for citations, and provides robust
error handling and retry logic.
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import aiohttp
from aiohttp import ClientTimeout
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from ..core.config import Settings

# Configure logging
logger = logging.getLogger(__name__)

class OpenAIResponsesAPI:
    """
    OpenAI Responses API client with web search capabilities.
    
    This class provides methods to interact with OpenAI's Responses API,
    enabling web search for real-time information and citations.
    """
    
    def __init__(self, config: Optional[Settings] = None):
        """
        Initialize the OpenAI Responses API client.
        
        Args:
            config: Settings instance. If None, creates a new instance.
        """
        self.config = config or Settings()
        self.base_url = "https://api.openai.com/v1/assistants"
        self.responses_url = "https://api.openai.com/v1/threads"
        
        # Validate configuration
        if not self.config.has_openai_config:
            raise ValueError("OpenAI API key not configured")
        
        self.headers = {
            "Authorization": f"Bearer {self.config.OPENAI_API_KEY}",
            "Content-Type": "application/json",
            "OpenAI-Beta": "assistants=v2"
        }
        
        # Default timeout
        self.timeout = ClientTimeout(total=self.config.OPENAI_SEARCH_TIMEOUT)
    
    async def create_assistant_with_web_search(
        self,
        name: str,
        instructions: str,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create an assistant with web search capabilities.
        
        Args:
            name: Name of the assistant
            instructions: System instructions for the assistant
            model: Model to use (defaults to config setting)
            
        Returns:
            Assistant creation response
        """
        model = model or self.config.OPENAI_RESPONSES_MODEL
        
        payload = {
            "name": name,
            "instructions": instructions,
            "model": model,
            "tools": [
                {
                    "type": "web_search",
                    "web_search": {
                        "version": self.config.OPENAI_WEB_SEARCH_TOOL_VERSION
                    }
                }
            ]
        }
        
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            async with session.post(
                f"{self.base_url}",
                headers=self.headers,
                json=payload
            ) as response:
                if response.status == 201:
                    return await response.json()
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to create assistant: {response.status} - {error_text}")
                    raise Exception(f"Assistant creation failed: {error_text}")
    
    async def create_thread(self) -> Dict[str, Any]:
        """
        Create a new conversation thread.
        
        Returns:
            Thread creation response
        """
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            async with session.post(
                f"{self.responses_url}",
                headers=self.headers
            ) as response:
                if response.status == 201:
                    return await response.json()
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to create thread: {response.status} - {error_text}")
                    raise Exception(f"Thread creation failed: {error_text}")
    
    async def add_message_to_thread(
        self,
        thread_id: str,
        content: str,
        role: str = "user"
    ) -> Dict[str, Any]:
        """
        Add a message to a thread.
        
        Args:
            thread_id: ID of the thread
            content: Message content
            role: Message role (user or assistant)
            
        Returns:
            Message creation response
        """
        payload = {
            "role": role,
            "content": content
        }
        
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            async with session.post(
                f"{self.responses_url}/{thread_id}/messages",
                headers=self.headers,
                json=payload
            ) as response:
                if response.status == 201:
                    return await response.json()
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to add message: {response.status} - {error_text}")
                    raise Exception(f"Message creation failed: {error_text}")
    
    async def run_assistant(
        self,
        thread_id: str,
        assistant_id: str,
        instructions: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Run an assistant on a thread.
        
        Args:
            thread_id: ID of the thread
            assistant_id: ID of the assistant
            instructions: Optional additional instructions
            
        Returns:
            Run creation response
        """
        payload = {
            "assistant_id": assistant_id
        }
        
        if instructions:
            payload["instructions"] = instructions
        
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            async with session.post(
                f"{self.responses_url}/{thread_id}/runs",
                headers=self.headers,
                json=payload
            ) as response:
                if response.status == 201:
                    return await response.json()
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to run assistant: {response.status} - {error_text}")
                    raise Exception(f"Assistant run failed: {error_text}")
    
    async def get_run_status(
        self,
        thread_id: str,
        run_id: str
    ) -> Dict[str, Any]:
        """
        Get the status of a run.
        
        Args:
            thread_id: ID of the thread
            run_id: ID of the run
            
        Returns:
            Run status response
        """
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            async with session.get(
                f"{self.responses_url}/{thread_id}/runs/{run_id}",
                headers=self.headers
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to get run status: {response.status} - {error_text}")
                    raise Exception(f"Run status check failed: {error_text}")
    
    async def get_thread_messages(
        self,
        thread_id: str,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Get messages from a thread.
        
        Args:
            thread_id: ID of the thread
            limit: Number of messages to retrieve
            
        Returns:
            Messages response
        """
        params = {"limit": limit}
        
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            async with session.get(
                f"{self.responses_url}/{thread_id}/messages",
                headers=self.headers,
                params=params
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to get messages: {response.status} - {error_text}")
                    raise Exception(f"Message retrieval failed: {error_text}")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((aiohttp.ClientError, asyncio.TimeoutError))
    )
    async def get_response_with_web_search(
        self,
        system_prompt: str,
        user_prompt: str,
        assistant_name: str = "AI Assistant",
        model: Optional[str] = None,
        max_retries: int = 3,
        polling_interval: float = 1.0
    ) -> Dict[str, Any]:
        """
        Get a response from OpenAI with web search capabilities.
        
        This is the main method that orchestrates the entire flow:
        1. Creates an assistant with web search
        2. Creates a thread
        3. Adds the user message
        4. Runs the assistant
        5. Polls for completion
        6. Retrieves the response with citations
        
        Args:
            system_prompt: System instructions for the assistant
            user_prompt: User's question or prompt
            assistant_name: Name for the assistant
            model: Model to use (defaults to config setting)
            max_retries: Maximum number of retries for polling
            polling_interval: Interval between status checks (seconds)
            
        Returns:
            Dictionary containing:
            - success: Boolean indicating success
            - response: The assistant's response
            - citations: List of web search citations
            - thread_id: Thread ID for future reference
            - assistant_id: Assistant ID for future reference
            - error: Error message if failed
        """
        try:
            # Step 1: Create assistant with web search
            logger.info("Creating assistant with web search capabilities")
            assistant_response = await self.create_assistant_with_web_search(
                name=assistant_name,
                instructions=system_prompt,
                model=model
            )
            assistant_id = assistant_response["id"]
            
            # Step 2: Create thread
            logger.info("Creating conversation thread")
            thread_response = await self.create_thread()
            thread_id = thread_response["id"]
            
            # Step 3: Add user message
            logger.info("Adding user message to thread")
            await self.add_message_to_thread(
                thread_id=thread_id,
                content=user_prompt,
                role="user"
            )
            
            # Step 4: Run assistant
            logger.info("Running assistant")
            run_response = await self.run_assistant(
                thread_id=thread_id,
                assistant_id=assistant_id
            )
            run_id = run_response["id"]
            
            # Step 5: Poll for completion
            logger.info("Polling for run completion")
            for attempt in range(max_retries * 10):  # More granular polling
                await asyncio.sleep(polling_interval)
                
                status_response = await self.get_run_status(
                    thread_id=thread_id,
                    run_id=run_id
                )
                
                status = status_response["status"]
                logger.debug(f"Run status: {status}")
                
                if status == "completed":
                    break
                elif status in ["failed", "cancelled", "expired"]:
                    raise Exception(f"Run failed with status: {status}")
                elif status == "requires_action":
                    # Handle tool calls if needed
                    logger.info("Run requires action - handling tool calls")
                    # For now, we'll let it continue
                    continue
                
                if attempt >= max_retries * 10 - 1:
                    raise Exception("Run timed out")
            
            # Step 6: Get messages with citations
            logger.info("Retrieving response with citations")
            messages_response = await self.get_thread_messages(
                thread_id=thread_id,
                limit=5
            )
            
            # Extract the latest assistant message
            messages = messages_response.get("data", [])
            assistant_message = None
            
            for message in messages:
                if message["role"] == "assistant":
                    assistant_message = message
                    break
            
            if not assistant_message:
                raise Exception("No assistant response found")
            
            # Extract response content and citations
            response_content = ""
            citations = []
            
            for content_item in assistant_message["content"]:
                if content_item["type"] == "text":
                    response_content += content_item["text"]["value"]
                    
                    # Extract citations from annotations
                    annotations = content_item["text"].get("annotations", [])
                    for annotation in annotations:
                        if annotation["type"] == "file_citation":
                            citations.append({
                                "type": "citation",
                                "file_id": annotation["file_citation"]["file_id"],
                                "quote": annotation["file_citation"].get("quote", ""),
                                "start_index": annotation["start_index"],
                                "end_index": annotation["end_index"]
                            })
            
            return {
                "success": True,
                "response": response_content,
                "citations": citations,
                "thread_id": thread_id,
                "assistant_id": assistant_id,
                "run_id": run_id,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in get_response_with_web_search: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "response": None,
                "citations": [],
                "thread_id": None,
                "assistant_id": None,
                "run_id": None,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def cleanup_resources(
        self,
        thread_id: Optional[str] = None,
        assistant_id: Optional[str] = None
    ) -> Dict[str, bool]:
        """
        Clean up resources (thread and assistant).
        
        Args:
            thread_id: Thread ID to delete
            assistant_id: Assistant ID to delete
            
        Returns:
            Dictionary with cleanup results
        """
        results = {"thread_deleted": False, "assistant_deleted": False}
        
        try:
            # Delete thread if provided
            if thread_id:
                async with aiohttp.ClientSession(timeout=self.timeout) as session:
                    async with session.delete(
                        f"{self.responses_url}/{thread_id}",
                        headers=self.headers
                    ) as response:
                        results["thread_deleted"] = response.status == 204
            
            # Delete assistant if provided
            if assistant_id:
                async with aiohttp.ClientSession(timeout=self.timeout) as session:
                    async with session.delete(
                        f"{self.base_url}/{assistant_id}",
                        headers=self.headers
                    ) as response:
                        results["assistant_deleted"] = response.status == 204
                        
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
        
        return results


# Convenience function for quick usage
async def get_openai_response_with_citations(
    system_prompt: str,
    user_prompt: str,
    assistant_name: str = "AI Assistant",
    model: Optional[str] = None
) -> Dict[str, Any]:
    """
    Convenience function to get OpenAI response with web search citations.
    
    Args:
        system_prompt: System instructions
        user_prompt: User's question
        assistant_name: Name for the assistant
        model: Model to use
        
    Returns:
        Response dictionary with citations
    """
    client = OpenAIResponsesAPI()
    return await client.get_response_with_web_search(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        assistant_name=assistant_name,
        model=model
    )


# Example usage and testing
async def test_openai_responses_api():
    """
    Test function to demonstrate usage of the OpenAI Responses API.
    """
    # Example system and user prompts
    system_prompt = """You are a helpful AI assistant with access to real-time web search. 
    When answering questions, use web search to find current information and provide citations 
    for your sources. Always be accurate and up-to-date."""
    
    user_prompt = "What are the latest developments in AI technology as of 2024?"
    
    try:
        # Create client
        client = OpenAIResponsesAPI()
        
        # Get response with citations
        result = await client.get_response_with_web_search(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            assistant_name="AI Research Assistant"
        )
        
        if result["success"]:
            print("✅ Success!")
            print(f"Response: {result['response']}")
            print(f"Citations: {len(result['citations'])} found")
            for i, citation in enumerate(result['citations'], 1):
                print(f"  Citation {i}: {citation}")
            
            # Cleanup
            await client.cleanup_resources(
                thread_id=result['thread_id'],
                assistant_id=result['assistant_id']
            )
        else:
            print(f"❌ Error: {result['error']}")
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")


if __name__ == "__main__":
    # Run test if executed directly
    asyncio.run(test_openai_responses_api())
