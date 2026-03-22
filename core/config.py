from pathlib import Path
from pydantic import PrivateAttr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from langchain_groq.chat_models import ChatGroq
from langchain_cohere import ChatCohere, CohereEmbeddings
from langchain_openai import AzureChatOpenAI  # noqa: F401
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings

from core.logger import logger


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="core/.env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Provider API Keys (optional — add new ones here, they auto-export to os.environ)
    GROQ_API_KEY: str = ""
    COHERE_API_KEY: str = ""

    # Azure OpenAI Configurations
    AZURE_OPENAI_API_KEY: str = ""
    AZURE_OPENAI_ENDPOINT: str = ""
    AZURE_OPENAI_DEPLOYMENT: str = "gpt-4o-mini"
    AZURE_OPENAI_API_VERSION: str = "2024-12-01-preview"

    # Vector Database
    QDRANT_URL: str = ""
    QDRANT_API_KEY: str = ""
    VECTOR_COLLECTION: str = "portfolio"

    # Other Configurations
    DATA_DIR: str = "data"
    PORT: str = "80"

    _models_cache: dict = PrivateAttr(default_factory=dict)

    @property
    def _providers(self) -> dict[str, dict]:
        return {
            "llm": {
                "azure_openai": {
                    "cls": AzureChatOpenAI,
                    "kwargs": {
                        "azure_deployment": self.AZURE_OPENAI_DEPLOYMENT,
                        "temperature": 0,
                        "streaming": True,
                        "azure_endpoint": self.AZURE_OPENAI_ENDPOINT,
                        "api_version": self.AZURE_OPENAI_API_VERSION,
                        "api_key": self.AZURE_OPENAI_API_KEY,
                    },
                },
                "cohere": {
                    "cls": ChatCohere,
                    "kwargs": {"model": "command-a-03-2025", "temperature": 0, "streaming": True, "cohere_api_key": self.COHERE_API_KEY},
                },
                "groq": {
                    "cls": ChatGroq,
                    "kwargs": {"model": "llama-3.1-8b-instant", "temperature": 0, "streaming": True, "groq_api_key": self.GROQ_API_KEY},
                },
            },
            "embedding": {
                "cohere": {
                    "cls": CohereEmbeddings,
                    "kwargs": {"model": "embed-english-v3.0", "cohere_api_key": self.COHERE_API_KEY},
                },
            },
        }

    @model_validator(mode="after")
    def _validate_qdrant(self) -> "Settings":
        if not self.QDRANT_URL or not self.QDRANT_API_KEY:
            raise ValueError(
                "QDRANT_URL and QDRANT_API_KEY are required. Set them in environment"
            )
        return self

    @model_validator(mode="after")
    def _setup_dirs(self) -> "Settings":
        """Create required directories."""
        Path(self.DATA_DIR).mkdir(parents=True, exist_ok=True)
        return self

    def _load_models(self):
        """Load every models available in config and cache them."""
        _available_models = []          # Only for logger to know which models were loaded successfully

        for model_type, provider_details in self._providers.items():
            self._models_cache.setdefault(model_type, {})
            for provider, kwargs in provider_details.items():
                try:
                    cls = kwargs["cls"]
                    model_kwargs = kwargs["kwargs"]

                    # Skip if any kwarg value is blank (unset env var)
                    missing = [k for k, v in model_kwargs.items() if v == ""]
                    if missing:
                        logger.warning(f"Skipping {provider} ({model_type}): missing values for {', '.join(missing)}. Set them in your .env file.")
                        continue

                    instance = cls(**model_kwargs)
                    self._models_cache[model_type][provider] = instance

                    model_name = model_kwargs.get("model") or model_kwargs.get("azure_deployment", "unknown")
                    _available_models.append(f"{model_type}:{provider}:{model_name}")
                except Exception as e:
                    logger.error(f"Failed to load model {provider} for {model_type}: {(e)}")

        logger.info(f"Loaded models: {_available_models}")

        if not _available_models:
            logger.warning("No models were loaded successfully. Check your configuration and API keys.")
            raise ValueError("""No models loaded successfully. Atleast one llm & one embedder must be loaded for the application to function.""")
        
        # Check that at least one model of each type is loaded
        for model_type in self._models_cache:
            if not self._models_cache[model_type]:
                logger.warning(f"No models loaded for type '{model_type}'. At least one model of this type must be loaded for the application to function.")
                raise ValueError(f"No models loaded for type '{model_type}'. At least one model of this type must be loaded for the application to function.")
    

    def get_llm(self, provider: str | None = None) -> BaseChatModel:

        if provider and provider in self._models_cache["llm"]:
            return self._models_cache["llm"][provider]
        
        logger.warning(f"Requested LLM provider '{provider}' not found. Available providers: {list(self._models_cache['llm'].keys())}. Selecting first available provider.")
        
        # If no provider specified or requested provider not found, return the first available LLM
        if self._models_cache["llm"]:
            # Return the first available LLM if no provider specified
            selected_llm = list(self._models_cache["llm"].values())[0]
            logger.info(f"Selected LLM: {selected_llm}")
            return selected_llm
        else:
            raise ValueError("No LLM providers are configured.")


    def get_embedder(self, provider: str | None = None) -> Embeddings:
        if provider and provider in self._models_cache["embedding"]:
            return self._models_cache["embedding"][provider]
        
        logger.warning(f"Requested embedder provider '{provider}' not found. Available providers: {list(self._models_cache['embedding'].keys())}. Selecting first available provider.")
        
        # If no provider specified or requested provider not found, return the first available embedder
        if self._models_cache["embedding"]:
            # Return the first available embedder if no provider specified
            selected_embedder = list(self._models_cache["embedding"].values())[0]
            logger.info(f"Selected embedder: {selected_embedder.model}")
            return selected_embedder
        else:
            raise ValueError("No embedder providers are configured.")


settings = Settings()
