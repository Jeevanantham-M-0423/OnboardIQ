import logging
import time

from fastapi import FastAPI
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware

from app.services.dataset_enricher import enrich_datasets

logger = logging.getLogger("onboardiq.api")
logging.basicConfig(level=logging.INFO)

try:
  enrich_datasets()
except Exception:
  logger.exception("Dataset enrichment failed. Falling back to existing static data.")

from app.routes.upload import router as upload_router

app = FastAPI(title="AI-Adaptive Onboarding Engine API")

app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
  start = time.perf_counter()
  logger.info("Request start: %s %s", request.method, request.url.path)

  try:
    response = await call_next(request)
  except Exception:
    logger.exception("Request error: %s %s", request.method, request.url.path)
    raise

  duration_ms = (time.perf_counter() - start) * 1000
  logger.info(
    "Request end: %s %s status=%s duration_ms=%.2f",
    request.method,
    request.url.path,
    response.status_code,
    duration_ms,
  )
  return response


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(upload_router)
