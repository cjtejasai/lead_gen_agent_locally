from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime
import time
from loguru import logger
from anthropic import Anthropic
from openai import OpenAI

from app.core.config import settings


class BaseAgent(ABC):
    """
    Base class for all LLM-based agents
    """

    def __init__(
        self,
        name: str,
        model: str = "gpt-4-turbo-preview",
        provider: str = "openai",
        temperature: float = 0.7,
    ):
        self.name = name
        self.model = model
        self.provider = provider
        self.temperature = temperature

        # Initialize LLM clients
        if provider == "openai":
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        elif provider == "anthropic":
            self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        Get the system prompt for this agent
        """
        pass

    @abstractmethod
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input data and return results
        """
        pass

    def call_llm(
        self,
        messages: list,
        temperature: Optional[float] = None,
        max_tokens: int = 4000,
    ) -> str:
        """
        Call the LLM with messages and return response
        """
        temp = temperature if temperature is not None else self.temperature

        try:
            if self.provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temp,
                    max_tokens=max_tokens,
                )
                return response.choices[0].message.content

            elif self.provider == "anthropic":
                # Anthropic requires system message separately
                system_msg = next(
                    (m["content"] for m in messages if m["role"] == "system"), ""
                )
                user_messages = [m for m in messages if m["role"] != "system"]

                response = self.client.messages.create(
                    model=self.model,
                    system=system_msg,
                    messages=user_messages,
                    temperature=temp,
                    max_tokens=max_tokens,
                )
                return response.content[0].text

        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            raise

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent with timing and error handling
        """
        start_time = time.time()
        logger.info(f"Agent '{self.name}' starting execution")

        try:
            results = self.process(input_data)
            processing_time = time.time() - start_time

            logger.info(
                f"Agent '{self.name}' completed in {processing_time:.2f}s"
            )

            return {
                "agent_name": self.name,
                "results": results,
                "model_used": self.model,
                "processing_time": processing_time,
                "timestamp": datetime.utcnow().isoformat(),
                "success": True,
            }

        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Agent '{self.name}' failed: {e}")

            return {
                "agent_name": self.name,
                "error": str(e),
                "model_used": self.model,
                "processing_time": processing_time,
                "timestamp": datetime.utcnow().isoformat(),
                "success": False,
            }
