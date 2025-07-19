import os
from langchain.chat_models import ChatOpenAI, ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI

def get_llm(provider: str):
    """
    Return a LangChain chat model instance based on the provider name.

    Supported providers:
        - "openai"
        - "anthropic"
        - "gemini"

    Raises:
        ValueError if the provider is unsupported.
    """

    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("Missing OPENAI_API_KEY environment variable")
        return ChatOpenAI(
            model_name="gpt-4",
            openai_api_key=api_key,
            temperature=0.3
        )

    elif provider == "anthropic":
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("Missing ANTHROPIC_API_KEY environment variable")
        return ChatAnthropic(
            model="claude-3",
            anthropic_api_key=api_key,
            temperature=0.3
        )

    elif provider == "gemini":
        api_key = "AIzaSyC98llS8Qb1QCcMtHJV8G3NlJKQ0ujgHvI"
        if not api_key:
            raise ValueError("Missing GOOGLE_API_KEY environment variable")
        return ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=api_key,
            temperature=0.3
        )

    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")

# Example usage
if __name__ == "__main__":
    llm_provider = "gemini"  # or "openai", "anthropic"
    llm = get_llm(llm_provider)
    response = llm.predict("Hello, world!")
    print(response)
