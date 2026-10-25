from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.tickets import router
from app.database.database import async_session, engine
from app.services.classifier import classify
from app.services.errors import ConflictError, InvalidInputError, NotFoundError
from app.services.processing import ProcessingRuntime
from app.services.text_validation import TokenizerUnavailableError


@asynccontextmanager
async def lifespan(app: FastAPI):
    runtime = ProcessingRuntime(async_session, classifier=classify)
    await runtime.start(engine)
    app.state.processing_runtime = runtime
    try:
        yield
    finally:
        await runtime.stop()
        await engine.dispose()


app = FastAPI(lifespan=lifespan)
app.include_router(router)


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
