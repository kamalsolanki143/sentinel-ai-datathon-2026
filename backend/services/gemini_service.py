"""
Sentinel AI - Gemini Service
==============================
File: backend/services/gemini_service.py
Purpose: Wrapper service for interacting with the Google Gemini API.
         Provides structured responses, streaming, and retry mechanisms.

Dependencies: google-genai, tenacity, loguru
"""

from typing import Any, AsyncGenerator, Optional
from pydantic import BaseModel
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential
from google import genai
from google.genai import types

from backend.config.settings import get_settings

settings = get_settings()


class GeminiService:
    """Service for interacting with Google Gemini API."""

    def __init__(self) -> None:
        """Initialize the Gemini client with API key from settings."""
        self.api_key = settings.GEMINI_API_KEY
        self.model = settings.GEMINI_MODEL
        if not self.api_key:
            logger.warning("GEMINI_API_KEY is not set. API calls will fail.")
        
        # Initialize the official google-genai client
        self.client = genai.Client(api_key=self.api_key) if self.api_key else None
        
        # Default safety settings - adjustable based on requirements
        self.default_safety = [
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
                threshold=types.HarmBlockThreshold.BLOCK_ONLY_HIGH,
            ),
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                threshold=types.HarmBlockThreshold.BLOCK_ONLY_HIGH,
            ),
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                threshold=types.HarmBlockThreshold.BLOCK_ONLY_HIGH,
            ),
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=types.HarmBlockThreshold.BLOCK_ONLY_HIGH,
            ),
        ]

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def generate_text(
        self, 
        prompt: str, 
        system_instruction: Optional[str] = None,
        temperature: Optional[float] = None,
    ) -> str:
        """
        Generate text response using Gemini API with retry logic.
        """
        if not self.client:
            raise ValueError("Gemini client is not initialized (missing API key)")
            
        logger.debug(f"Generating text with model {self.model}")
        
        temp = temperature if temperature is not None else settings.GEMINI_TEMPERATURE
        config = types.GenerateContentConfig(
            temperature=temp,
            safety_settings=self.default_safety,
        )
        if system_instruction:
            config.system_instruction = system_instruction
            
        try:
            # Using async client method
            response = await self.client.aio.models.generate_content(
                model=self.model,
                contents=prompt,
                config=config,
            )
            return response.text
        except Exception as exc:
            logger.error(f"Error calling Gemini API: {str(exc)}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def generate_structured(
        self, 
        prompt: str, 
        response_schema: type[BaseModel],
        system_instruction: Optional[str] = None,
    ) -> Any:
        """
        Generate a structured JSON response matching a Pydantic schema.
        """
        if not self.client:
            raise ValueError("Gemini client is not initialized (missing API key)")
            
        logger.debug(f"Generating structured response for schema {response_schema.__name__}")
        
        config = types.GenerateContentConfig(
            temperature=0.1,  # Lower temperature for structured output
            response_mime_type="application/json",
            response_schema=response_schema,
            safety_settings=self.default_safety,
        )
        
        if system_instruction:
            config.system_instruction = system_instruction
            
        try:
            response = await self.client.aio.models.generate_content(
                model=self.model,
                contents=prompt,
                config=config,
            )
            
            # The google-genai client currently returns JSON text which needs validation
            # depending on the exact version, parsed object might be accessible
            text = response.text
            return response_schema.model_validate_json(text)
        except Exception as exc:
            logger.error(f"Error generating structured response: {str(exc)}")
            raise

    async def generate_stream(
        self, 
        prompt: str, 
        system_instruction: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        """
        Stream the response from Gemini API.
        """
        if not self.client:
            raise ValueError("Gemini client is not initialized (missing API key)")
            
        logger.debug("Starting streaming response")
        
        config = types.GenerateContentConfig(
            temperature=settings.GEMINI_TEMPERATURE,
            safety_settings=self.default_safety,
        )
        if system_instruction:
            config.system_instruction = system_instruction
            
        try:
            async for chunk in await self.client.aio.models.generate_content_stream(
                model=self.model,
                contents=prompt,
                config=config,
            ):
                if chunk.text:
                    yield chunk.text
        except Exception as exc:
            logger.error(f"Error streaming from Gemini API: {str(exc)}")
            raise
