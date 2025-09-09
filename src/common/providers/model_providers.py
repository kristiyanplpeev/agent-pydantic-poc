import os
from pydantic_ai.providers.google import GoogleProvider
from pydantic_ai.providers.anthropic import AnthropicProvider
from pydantic_ai.providers.openai import OpenAIProvider

openai_key = os.environ["OPENAI_API_KEY"]
google_key = os.environ["GOOGLE_API_KEY"]
anthropic_key = os.environ["ANTHROPIC_API_KEY"]

google_provider = GoogleProvider(api_key=google_key)
anthropic_provider = AnthropicProvider(api_key=anthropic_key)
openai_provider = OpenAIProvider(api_key=openai_key)
