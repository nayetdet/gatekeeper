from datetime import datetime
from pathlib import Path
from typing import Optional
from gatekeeper.runtime import START_TIME

class FileUtils:
    @classmethod
    def get_directory_path(cls, base_directory: Optional[Path] = None, dt: Optional[datetime] = None) -> Path:
        dirname: str = cls.get_timestamp(dt)
        path: Path = (base_directory or Path.cwd()) / dirname
        path.mkdir(parents=True, exist_ok=True)
        return path

    @classmethod
    def get_file_path(cls, extension: str, base_directory: Optional[Path] = None, dt: Optional[datetime] = None) -> Path:
        directory: Path = base_directory or Path.cwd()
        directory.mkdir(parents=True, exist_ok=True)
        suffix: str = extension if extension.startswith(".") else f".{extension}"
        return (directory / cls.get_timestamp(dt)).with_suffix(suffix)

    @staticmethod
    def get_timestamp(dt: Optional[datetime] = None) -> str:
        return f"{(dt if dt is not None else START_TIME):%Y%m%dT%H%M%S%f}"
