from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.api.tickets import router
from app.api.auth import router as auth_router
from app.database.database import async_session, engine
from app.services.classifier import classify
from app.services.errors import AuthenticationError, ForbiddenError, ConflictError, InvalidInputError, NotFoundError
from app.services.auth import jwt_secret
from app.services.processing import ProcessingRuntime
from app.services.text_validation import TokenizerUnavailableError
from app.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    jwt_secret()
    runtime = ProcessingRuntime(async_session, classifier=classify)
    await runtime.start(engine)
    app.state.processing_runtime = runtime
    try:
        yield
    finally:
        await runtime.stop()
        await engine.dispose()


app = FastAPI(lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=settings.CORS_ORIGINS,
                   allow_methods=["GET", "POST", "PATCH", "DELETE"],
                   allow_headers=["Authorization", "Content-Type"])
app.include_router(router)
app.include_router(auth_router)


@app.exception_handler(AuthenticationError)
async def authentication_error_handler(request: Request, exc: AuthenticationError):
    return JSONResponse(status_code=401, content={"detail": str(exc)}, headers={"WWW-Authenticate": "Bearer"})


@app.exception_handler(ForbiddenError)
async def forbidden_error_handler(request: Request, exc: ForbiddenError):
    return JSONResponse(status_code=403, content={"detail": str(exc)})


@app.exception_handler(TokenizerUnavailableError)
async def tokenizer_error_handler(request: Request, exc: TokenizerUnavailableError):
    return JSONResponse(status_code=503, content={"detail": str(exc)})


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        context = error.get("ctx", {})
        message = str(context["error"]) if "error" in context else "Niepoprawna lub brakująca wartość."
        errors.append({"loc": list(error["loc"]), "type": error["type"], "msg": message})
    return JSONResponse(status_code=422, content={"detail": errors})


@app.exception_handler(NotFoundError)
@app.exception_handler(ConflictError)
async def service_error_handler(request: Request, exc: NotFoundError | ConflictError):
    status_code = 404 if isinstance(exc, NotFoundError) else 409
    return JSONResponse(status_code=status_code, content={"detail": str(exc)})


@app.exception_handler(InvalidInputError)
async def invalid_input_handler(request: Request, exc: InvalidInputError):
    detail = str(exc)
    if exc.field is not None:
        detail = [{"loc": ["body", exc.field], "type": "value_error", "msg": str(exc)}]
    return JSONResponse(status_code=422, content={"detail": detail})
