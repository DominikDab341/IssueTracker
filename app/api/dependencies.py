from fastapi import Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_db
from app.services.processing import ProcessingRuntime
from app.services.tickets import TicketService


def get_processing_runtime(request: Request) -> ProcessingRuntime:
    runtime = getattr(request.app.state, "processing_runtime", None)
    if runtime is None:
        raise HTTPException(status_code=503, detail="Przetwarzanie nie jest gotowe.")
    return runtime


async def get_ticket_service(db: AsyncSession = Depends(get_db)) -> TicketService:
    return TicketService(db)
