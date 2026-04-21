"""Application settings loaded from environment and optional backend/.env."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Annotated, Any

from pydantic import BeforeValidator, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _split_cors(v: Any) -> list[str]:
    if v is None:
        return []
    if isinstance(v, list):
        return [str(x).strip() for x in v if str(x).strip()]
    s = str(v).strip()
    if not s:
        return []
    return [part.strip() for part in s.split(",") if part.strip()]


CorsOrigins = Annotated[list[str], BeforeValidator(_split_cors)]


_DEFAULT_CORS = (
    "http://localhost:3000,"
    "http://127.0.0.1:3000,"
    "https://carparkho.vercel.app"
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    repo_root: Path = Field(
        default_factory=lambda: Path(__file__).resolve().parent.parent,
        description="Repository root (parent of backend/).",
    )

    cars_dataset_path: Path | None = None
    questions_config_path: Path | None = None
    scoring_config_path: Path | None = None

    openrouter_api_key: str | None = None
    openrouter_model: str = "google/gemini-2.0-flash-001"
    openrouter_base_url: str = "https://openrouter.ai/api/v1/chat/completions"
    openrouter_timeout_seconds: float = 30.0

    cors_origins: CorsOrigins = Field(default=_DEFAULT_CORS)
    log_level: str = "INFO"

    @model_validator(mode="after")
    def _defaults_and_log_level(self) -> Settings:
        backend_dir = Path(__file__).resolve().parent
        if self.cars_dataset_path is None:
            self.cars_dataset_path = backend_dir / "cars-dataset.json"
        if self.questions_config_path is None:
            self.questions_config_path = backend_dir / "questions-config.json"
        if self.scoring_config_path is None:
            self.scoring_config_path = backend_dir / "scoring-config.json"

        level_name = (self.log_level or "INFO").upper()
        if level_name not in logging._nameToLevel:
            self.log_level = "INFO"
        else:
            self.log_level = level_name

        return self
