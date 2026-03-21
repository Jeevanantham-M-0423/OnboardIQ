from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status

from app.config import ALLOWED_EXTENSIONS, ALLOWED_MIME_TYPES, MAX_UPLOAD_SIZE_BYTES


def _validate_extension(upload: UploadFile, field_name: str) -> str:
    suffix = Path(upload.filename or "").suffix.lower()

    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Invalid file extension for '{field_name}'. "
                "Only PDF and DOCX are allowed."
            ),
        )

    return suffix


def _validate_mime_type(upload: UploadFile, field_name: str) -> None:
    content_type = (upload.content_type or "").lower()

    if content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Invalid MIME type for '{field_name}': '{content_type or 'unknown'}'. "
                "Only PDF and DOCX files are accepted."
            ),
        )


def save_validated_upload(upload: UploadFile, field_name: str, destination_dir: Path) -> Path:
    if not upload.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Missing filename for '{field_name}'.",
        )

    suffix = _validate_extension(upload, field_name)
    _validate_mime_type(upload, field_name)

    safe_filename = f"{uuid4().hex}{suffix}"
    destination_path = destination_dir / safe_filename

    total_size = 0

    try:
        upload.file.seek(0)

        with destination_path.open("wb") as out_file:
            while True:
                chunk = upload.file.read(1024 * 1024)
                if not chunk:
                    break

                total_size += len(chunk)
                if total_size > MAX_UPLOAD_SIZE_BYTES:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=(
                            f"'{field_name}' exceeds the 5MB size limit. "
                            "Please upload a smaller file."
                        ),
                    )

                out_file.write(chunk)
    except HTTPException:
        if destination_path.exists():
            destination_path.unlink()
        raise
    except Exception as exc:
        if destination_path.exists():
            destination_path.unlink()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process '{field_name}' file.",
        ) from exc

    return destination_path
