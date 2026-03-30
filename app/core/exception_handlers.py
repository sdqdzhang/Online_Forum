from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


def _payload(status: int, message: str, detail):
    return {
        "status": status,
        "message": message,
        "payload": detail,
    }


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(_: Request, exc: StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content=_payload(exc.status_code, "请求失败", exc.detail),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(_: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content=_payload(422, "参数校验失败", exc.errors()),
        )

    @app.exception_handler(Exception)
    async def internal_exception_handler(_: Request, __: Exception):
        return JSONResponse(
            status_code=500,
            content=_payload(500, "服务器内部错误", "请稍后重试或联系管理员"),
        )
