import os
from pydantic import model_validator, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from langchain_groq.chat_models import ChatGroq
from langchain_cohere import ChatCohere, CohereEmbeddings
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings

from core.logger import logger

DEFAULT_LLM_CONFIG: dict[str, dict] = {
    "cohere": {"cls": ChatCohere, "config": {"model": "command-a-03-2025", "temperature": 0, "streaming": True}},
    "groq": {"cls": ChatGroq, "config": {"model": "llama-3.1-8b-instant", "temperature": 0, "streaming": True}},
}

DEFAULT_EMBEDDING_CONFIG: dict[str, dict] = {
    "cohere": {"cls": CohereEmbeddings, "config": {"model": "embed-english-v3.0"}},
    "huggingface": {"cls": HuggingFaceEmbeddings, "config": {"model_name": "BAAI/bge-small-en-v1.5", "model_kwargs": {"device": "cpu"}, "encode_kwargs": {"normalize_embeddings": False}, "show_progress": False}},
}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="core/.env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    GROQ_API_KEY: str = ""
    COHERE_API_KEY: str = ""
    DEFAULT_LLM_PROVIDER: str = "cohere"
    LLM_CONFIG: dict[str, dict] = DEFAULT_LLM_CONFIG
    DEFAULT_EMBEDDING_PROVIDER: str = "cohere"
    EMBEDDING_CONFIG: dict[str, dict] = DEFAULT_EMBEDDING_CONFIG
    QDRANT_URL: str = ""
    QDRANT_API_KEY: str = ""
    VECTOR_COLLECTION: str = ""
    HF_TOKEN: str = ""
    DATA_DIR: str = "data"
    PORT: str = "8001"
    available_llms: dict = Field(default_factory=dict, exclude=True)
    available_embedders: dict = Field(default_factory=dict, exclude=True)

    @model_validator(mode="after")
    def check_non_blank(self) -> "Settings":
        blank_vars = [
            field
            for field in Settings.model_fields
            if getattr(self, field) == "" and Settings.model_fields[field].default == ""
        ]
        
        if blank_vars:
            raise ValueError(
                "The following environment variables are not set: "
                f"{', '.join(blank_vars)}. "
                "Please define them in your core/.env file."
            )
        return self

    @model_validator(mode="after")
    def load_into_env(self) -> "Settings":
        os.environ.setdefault("HF_TOKEN", self.HF_TOKEN)
        os.environ.setdefault("GROQ_API_KEY", self.GROQ_API_KEY)
        os.environ.setdefault("COHERE_API_KEY", self.COHERE_API_KEY)
        return self

    def load_llm(self, provider: str = None) -> BaseChatModel:
        """Load a specific provider's LLM, or try each in order and return the first that succeeds."""
        if provider and provider not in self.LLM_CONFIG:
            raise ValueError(
                f"Unknown provider '{provider}'. "
                f"Available: {list(self.LLM_CONFIG)}"
            )
        providers = {provider: self.LLM_CONFIG[provider]} if provider else self.LLM_CONFIG

        for provider, metadata in providers.items():
            cls = metadata.get("cls")
            if not cls:
                logger.warning("No 'cls' in config for provider '%s', skipping.", provider)
                continue
            try:
                self.available_llms[provider] = cls(**metadata.get("config", {}))
            except Exception as e:
                logger.warning("Cannot initialize provider '%s', skipped — %s", provider, e)
                continue

        if self.available_llms:
            logger.info("Successfully loaded LLM providers: %s", list(self.available_llms))
            return list(self.available_llms.values())[0]

        raise ValueError(f"No usable LLM provider. Tried: {list(providers)}")

    def load_embedder(self, provider: str = None) -> Embeddings:
        """Load a specific embedding provider, or try each in order and return the first that succeeds."""
        if provider and provider not in self.EMBEDDING_CONFIG:
            raise ValueError(
                f"Unknown embedding provider '{provider}'. "
                f"Available: {list(self.EMBEDDING_CONFIG)}"
            )
        providers = {provider: self.EMBEDDING_CONFIG[provider]} if provider else self.EMBEDDING_CONFIG

        for name, metadata in providers.items():
            cls = metadata.get("cls")
            if not cls:
                logger.warning("No 'cls' in embedding config for provider '%s', skipping.", name)
                continue
            try:
                self.available_embedders[name] = cls(**metadata.get("config", {}))
            except Exception as e:
                logger.warning("Cannot initialize embedding provider '%s', skipped — %s", name, e)
                continue

        if self.available_embedders:
            logger.info("Successfully loaded embedding providers: %s", list(self.available_embedders))
            return list(self.available_embedders.values())[0]

        raise ValueError(f"No usable embedding provider. Tried: {list(providers)}")

    def get_llm(self, provider: str = None) -> BaseChatModel:
        """Get an already-loaded LLM. Falls back to the first available."""
        if provider:
            if provider in self.available_llms:
                return self.available_llms[provider]
            raise ValueError(f"LLM provider '{provider}' not loaded. Loaded: {list(self.available_llms)}")
        if self.available_llms:
            return list(self.available_llms.values())[0]
        raise ValueError("No LLMs loaded. Call load_llm() during startup first.")

    def get_embedder(self, provider: str = None) -> Embeddings:
        """Get an already-loaded embedder. Falls back to the first available."""
        if provider:
            if provider in self.available_embedders:
                return self.available_embedders[provider]
            raise ValueError(f"Embedding provider '{provider}' not loaded. Loaded: {list(self.available_embedders)}")
        if self.available_embedders:
            return list(self.available_embedders.values())[0]
        raise ValueError("No embedders loaded. Call load_embedder() during startup first.")


settings = Settings()
