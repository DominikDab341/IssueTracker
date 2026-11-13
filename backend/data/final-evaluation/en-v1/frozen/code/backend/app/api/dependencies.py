from fastapi import Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordBearer

from app.database.database import get_db
from app.services.processing import ProcessingRuntime
from app.services.tickets import TicketService
from app.models.models import User
from app.services.auth import read_access_token
from app.services.access import require_active, require_assistant_access
from app.services.errors import AuthenticationError


oauth2 = OAuth2PasswordBearer(tokenUrl="auth/token", auto_error=False)


async def get_current_user(token: str | None = Depends(oauth2), db: AsyncSession = Depends(get_db)) -> User:
    if token is None:
        raise AuthenticationError("Zaloguj się, aby skorzystać z tej funkcji.")
    user = await db.get(User, read_access_token(token))
    if user is None:
        raise AuthenticationError("Niepoprawny lub wygasły token. Zaloguj się ponownie.")
    require_active(user)
    return user


async def get_assistant_user(user: User = Depends(get_current_user)) -> User:
    require_assistant_access(user)
    return user


def get_processing_runtime(request: Request) -> ProcessingRuntime:
    runtime = getattr(request.app.state, "processing_runtime", None)
    if runtime is None:
        raise HTTPException(status_code=503, detail="Przetwarzanie nie jest gotowe.")
    return runtime


async def get_ticket_service(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)) -> TicketService:
    return TicketService(db, user)
