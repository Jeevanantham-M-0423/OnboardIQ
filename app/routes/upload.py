import asyncio
import logging
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse

from app.config import PIPELINE_TIMEOUT_SECONDS, UPLOADS_DIR
from app.services.pipeline import build_onboarding_pipeline
from app.utils.file_upload import save_validated_upload

router = APIRouter(tags=["upload"])
logger = logging.getLogger("onboardiq.api")


def _error_response(message: str, status_code: int = 400) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "error",
            "message": message,
        },
    )


@router.post("/upload")
async def upload_files(
    resume: UploadFile = File(...),
    job_description: UploadFile = File(...),
):
    saved_paths: list[Path] = []

    try:
        saved_paths.append(save_validated_upload(resume, "resume", UPLOADS_DIR))
        saved_paths.append(
            save_validated_upload(job_description, "job_description", UPLOADS_DIR)
        )
    except HTTPException as exc:
        logger.error("Upload validation failed: %s", exc.detail)
        return _error_response(str(exc.detail), status_code=exc.status_code)
    except Exception as exc:
        logger.exception("Unexpected upload error.")
        return _error_response("Unexpected error while uploading files.", status_code=500)

    if len(saved_paths) != 2:
        logger.error("Expected 2 uploaded files, got %s", len(saved_paths))
        return _error_response("Both resume and job description files are required.")

    for path in saved_paths:
        if not path.exists():
            logger.error("Uploaded file missing on disk: %s", path)
            return _error_response("Uploaded file could not be processed.", status_code=500)

    try:
        result = await asyncio.wait_for(
            asyncio.to_thread(build_onboarding_pipeline, saved_paths[0], saved_paths[1]),
            timeout=PIPELINE_TIMEOUT_SECONDS,
        )

        # Keep response fields consistent, even for edge cases like no skills found.
        return {
            "resume_skills": list(result.get("resume_skills", []) or []),
            "jd_skills": list(result.get("jd_skills", []) or []),
            "matched_skills": list(result.get("matched_skills", []) or []),
            "missing_skills": list(result.get("missing_skills", []) or []),
            "roadmap": list(result.get("roadmap", []) or []),
        }
    except asyncio.TimeoutError as exc:
        logger.error("Pipeline processing timed out after %s seconds.", PIPELINE_TIMEOUT_SECONDS)
        return _error_response("Processing timed out. Please try again.", status_code=504)
    except ValueError as exc:
        logger.error("Pipeline validation failed: %s", str(exc))
        return _error_response(str(exc), status_code=400)
    except HTTPException as exc:
        logger.error("Pipeline HTTP error: %s", exc.detail)
        return _error_response("Failed to process files.", status_code=exc.status_code)
    except Exception as exc:
        logger.exception("Pipeline processing failed.")
        return _error_response("Failed to process onboarding pipeline.", status_code=500)
    finally:
        for path in saved_paths:
            try:
                if path.exists():
                    path.unlink()
            except Exception:
                logger.warning("Failed to delete temporary upload: %s", path)
