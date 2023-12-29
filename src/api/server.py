import json
import time
import logging

from fastapi import FastAPI, exceptions, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from src.api import audit, carts, catalog, bottler, barrels, admin
from starlette.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Little Alchemy Shop",
    description="Little Alchemy Shop is a Python+FastAPI backend for a fantasy potion shop",
    version="0.0.1",
    terms_of_service="http://example.com/terms/",
    contact={"name": "r-nasc"},
)

origins = ["https://potion-exchange.vercel.app"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(audit.router)
app.include_router(carts.router)
app.include_router(catalog.router)
app.include_router(bottler.router)
app.include_router(barrels.router)
app.include_router(admin.router)


@app.exception_handler(exceptions.RequestValidationError)
@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc):
    logging.error(f"The client sent invalid data!: {exc}")
    exc_json = json.loads(exc.json())
    response = {"message": [], "data": None}
    for error in exc_json:
        response["message"].append(f"{error['loc']}: {error['msg']}")

    return JSONResponse(response, status_code=422)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.monotonic()
    response = await call_next(request)
    process_time = time.monotonic() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.get("/")
async def root():
    return {"message": "Welcome to the Little Alchemy Shop."}
