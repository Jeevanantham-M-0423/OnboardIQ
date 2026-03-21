import os
from pathlib import Path


BASE_DIR: Path = Path(__file__).resolve().parent.parent
UPLOADS_DIR: Path = Path(os.getenv("UPLOADS_DIR", str(BASE_DIR / "uploads")))
MAX_UPLOAD_SIZE_BYTES: int = int(os.getenv("MAX_UPLOAD_SIZE_BYTES", str(5 * 1024 * 1024)))
PIPELINE_TIMEOUT_SECONDS: int = int(os.getenv("PIPELINE_TIMEOUT_SECONDS", "15"))
ALLOWED_EXTENSIONS: set[str] = {".pdf", ".docx"}
ALLOWED_MIME_TYPES: set[str] = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}

# Ensure uploads directory exists at startup/import time.
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
