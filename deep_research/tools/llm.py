 
"""
LLM provider management supporting multiple providers.
Prioritizes Google Gemini by default, with support for Groq, Fireworks, and OpenAI.
"""

import os
from typing import Any, Literal, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_core.language_models import BaseChatModel

# Define supported providers type for clarity
ProviderType = Literal["gemini", "groq", "fireworks", "openai"]

class LLMProvider:
    """
    Manages LLM providers with the following priority (unless strictly overridden):
    1. Google Gemini (Default)
    2. Groq
    3. Fireworks (DeepSeek R1)
    4. OpenAI
    """
    
    def __init__(
        self,
        provider: Optional[ProviderType] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
    ):
        self.provider = provider or self._resolve_provider()
        self.api_key = api_key or self._get_api_key(self.provider)
        self.base_url = base_url or self._get_base_url(self.provider)
        self.model = model or self._get_default_model(self.provider)
        self.temperature = temperature

    def _resolve_provider(self) -> ProviderType:
        """
        Determines the active provider based on environment variables.
        Priority: Env Override > Google > Groq > Fireworks > OpenAI
        """
        # 1. Explicit Environment Override
        env_provider = os.getenv("LLM_PROVIDER", "").lower()
        if env_provider in ["gemini", "groq", "fireworks", "openai"]:
            return env_provider

        # 2. Default Priority Chain
        if os.getenv("GOOGLE_API_KEY"):
            return "gemini"
        if os.getenv("GROQ_API_KEY"):
            return "groq"
        if os.getenv("FIREWORKS_API_KEY"):
            return "fireworks"
        
        return "openai"

    def _get_api_key(self, provider: ProviderType) -> str:
        """Retrieves the API key for the selected provider."""
        key_map = {
            "gemini": "GOOGLE_API_KEY",
            "groq": "GROQ_API_KEY",
            "fireworks": "FIREWORKS_API_KEY",
            "openai": "OPENAI_API_KEY"
        }
        env_var = key_map.get(provider)
        return os.getenv(env_var, "") if env_var else ""

    def _get_base_url(self, provider: ProviderType) -> Optional[str]:
        """Retrieves the Base URL (needed for OpenAI-compatible endpoints)."""
        # Allow explicit override from env
        if os.getenv("OPENAI_ENDPOINT"):
            return os.getenv("OPENAI_ENDPOINT")

        if provider == "groq":
            return "https://api.groq.com/openai/v1"
        if provider == "fireworks":
            return "https://api.fireworks.ai/inference/v1"
        
        return None # Default for Gemini (handled by SDK) and OpenAI

    def _get_default_model(self, provider: ProviderType) -> str:
        """Determines the default model for the selected provider."""
        # Allow explicit override from env
        if os.getenv("CUSTOM_MODEL"):
            return os.getenv("CUSTOM_MODEL")

        if provider == "gemini":
            return "gemini-2.5-flash"
        if provider == "groq":
            # Llama 3.3 70B is the current standard versatile model on Groq
            return "openai/gpt-oss-120b"
        if provider == "fireworks":
            return "accounts/fireworks/models/deepseek-r1"
        
        return "gpt-4o-mini" # OpenAI Default
    
    def get_llm(self, **kwargs) -> BaseChatModel:
        """
        Get a configured LLM instance.
        
        Args:
            **kwargs: Override parameters like temperature, max_tokens, etc.
        """
        params = {
            "model": self.model,
            "temperature": kwargs.get("temperature", self.temperature),
            "api_key": self.api_key,
        }
        
        if "max_tokens" in kwargs:
            params["max_tokens"] = kwargs["max_tokens"]

        # --- Gemini Logic ---
        if self.provider == "gemini":
            return ChatGoogleGenerativeAI(**params)
        
        # --- OpenAI Compatible Logic (Groq, Fireworks, OpenAI) ---
        if self.base_url:
            params["base_url"] = self.base_url
            
        return ChatOpenAI(**params)
    
    def get_reasoning_llm(self) -> BaseChatModel:
        """Get LLM configured for reasoning tasks (higher temperature)."""
        return self.get_llm(temperature=0.9)
    
    def get_structured_llm(self) -> BaseChatModel:
        """Get LLM configured for structured output (lower temperature)."""
        return self.get_llm(temperature=0.3)


# --- Token Counting Utilities ---

def count_tokens(text: str, model: str = "gpt-4") -> int:
    """
    Count tokens in text using tiktoken (OpenAI estimation).
    Note: For Gemini and Llama, this is an approximation.
    """
    try:
        import tiktoken
        encoding_model = model if "gpt" in model else "gpt-4"
        encoding = tiktoken.encoding_for_model(encoding_model)
        return len(encoding.encode(text))
    except Exception:
        # Fallback: rough estimate
        return len(text) // 4


def truncate_to_tokens(text: str, max_tokens: int, model: str = "gpt-4") -> str:
    """
    Truncate text to a maximum number of tokens.
    """
    try:
        import tiktoken
        encoding_model = model if "gpt" in model else "gpt-4"
        encoding = tiktoken.encoding_for_model(encoding_model)
        tokens = encoding.encode(text)
        if len(tokens) <= max_tokens:
            return text
        return encoding.decode(tokens[:max_tokens])
    except Exception:
        # Fallback: rough character-based truncation
        max_chars = max_tokens * 4
        return text[:max_chars] if len(text) > max_chars else text 