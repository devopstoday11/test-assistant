"""Configuration models for test-assistant using Pydantic."""
from pathlib import Path
from typing import List, Optional, Literal
from pydantic import BaseModel, Field, field_validator
import yaml


class TestAssistantConfig(BaseModel):
    """Configuration model for test-assistant."""

    watch_path: str = Field(..., description="Directory path to watch for new files")
    claude_prompt: str = Field(..., description="Prompt to send to claude CLI")
    file_extensions: List[str] = Field(
        default_factory=list,
        description="List of file extensions to watch (empty list = all files)"
    )

    # New configuration options
    dry_run: bool = Field(
        default=False,
        description="If True, files are renamed but Claude CLI is not triggered"
    )

    timestamp_format: str = Field(
        default="mmddyy-HH-MM-SS-AMPM",
        description="Timestamp format for file renaming. Supported: mmddyy-HH-MM-SS-AMPM or mmddyy-HHMMSS-AMPM"
    )

    process_existing_files: bool = Field(
        default=False,
        description="If True, process existing files in watch directory on startup"
    )

    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(
        default="INFO",
        description="Logging level: DEBUG, INFO, WARNING, or ERROR"
    )

    file_stability_timeout: float = Field(
        default=5.0,
        description="Maximum seconds to wait for file size to stabilize (default: 5.0)"
    )

    file_stability_check_interval: float = Field(
        default=0.1,
        description="Interval in seconds between file size checks (default: 0.1)"
    )

    @field_validator('watch_path')
    @classmethod
    def validate_watch_path(cls, v: str) -> str:
        """Validate that watch_path is a valid directory."""
        path = Path(v).expanduser().resolve()
        if not path.exists():
            raise ValueError(f"Watch path does not exist: {v}")
        if not path.is_dir():
            raise ValueError(f"Watch path is not a directory: {v}")
        return str(path)

    @field_validator('file_extensions')
    @classmethod
    def validate_extensions(cls, v: List[str]) -> List[str]:
        """Ensure extensions start with a dot."""
        return [ext if ext.startswith('.') else f'.{ext}' for ext in v]

    @field_validator('timestamp_format')
    @classmethod
    def validate_timestamp_format(cls, v: str) -> str:
        """Validate timestamp format."""
        valid_formats = [
            "mmddyy-HH-MM-SS-AMPM",
            "mmddyy-HHMMSS-AMPM",
            "mmddyy-HH:MM:SS-AMPM"
        ]
        if v not in valid_formats:
            raise ValueError(
                f"Invalid timestamp format: {v}. "
                f"Valid formats: {', '.join(valid_formats)}"
            )
        return v

    @classmethod
    def from_yaml(cls, config_path: str) -> 'TestAssistantConfig':
        """Load configuration from YAML file."""
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
        return cls(**config_data)
