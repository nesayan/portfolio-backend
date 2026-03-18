import os
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="core/.env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    GROQ_API_KEY: str = ""
    LLM_MODEL: str = ""
    QDRANT_URL: str = ""
    QDRANT_API_KEY: str = ""
    VECTOR_COLLECTION: str = ""
    EMBEDDING_MODEL: str = ""
    EMBEDDING_PROVIDER: str = ""
    HF_TOKEN: str = ""
    DATA_DIR: str = ""

    @model_validator(mode="after")
    def check_non_blank(self) -> "Settings":
        blank_vars = [
            field for field in Settings.model_fields if getattr(self, field) == ""
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
        # Only export what third-party libs need from os.environ
        os.environ.setdefault("HF_TOKEN", self.HF_TOKEN)
        return self


settings = Settings()
