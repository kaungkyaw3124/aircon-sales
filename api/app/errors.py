import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

log = logging.getLogger(__name__)

CODES = {401: "unauthorized", 404: "not_found", 405: "method_not_allowed"}


def error(status: int, code: str, message: str) -> JSONResponse:
    return JSONResponse({"error": {"code": code, "message": message}}, status_code=status)


def install(app: FastAPI) -> None:
    @app.exception_handler(HTTPException)
    async def http_error(request: Request, exc: HTTPException):
        # detail may be {"code", "message"} (raised by our code) or a plain string (raised by Starlette)
        if isinstance(exc.detail, dict):
            return error(exc.status_code, exc.detail["code"], exc.detail["message"])
        return error(exc.status_code, CODES.get(exc.status_code, "http_error"), str(exc.detail))

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError):
        message = "; ".join(
            f"{'.'.join(str(p) for p in e['loc'] if p != 'body') or 'body'}: {e['msg'].lower()}" for e in exc.errors()
        )
        return error(422, "validation_error", message)

    @app.exception_handler(Exception)
    async def internal_error(request: Request, exc: Exception):
        log.exception("unhandled error on %s %s", request.method, request.url.path)
        return error(500, "internal_error", "Internal server error.")
