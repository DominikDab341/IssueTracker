from datetime import datetime

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_db
from app.models.models import Ticket
from app.celery_app import classify_ticket_task
from app.services.classifier import find_similar_open_tickets

from typing import Literal

class TicketStatusUpdate(BaseModel):
    status: Literal["open", "resolved" ,"closed"]

ALLOWED_TRANSITIONS = {
    "open": {"resolved", "closed"},
    "resolved": {"open", "closed"},
    "closed": {"open"},
}

class TicketCreate(BaseModel):
    text: str


class TicketResponse(BaseModel):
    id: int
    text: str
    category: str
    priority: str
    created_at: datetime
    updated_at: datetime
    status: str
    model_config = {"from_attributes": True}

class SuggestedDuplicate(BaseModel):
    id: int
    text: str
    similarity: float

class TicketCloseResponse(BaseModel):
    ticket: TicketResponse
    status: Literal["closed"]
    suggested_duplicates: list[SuggestedDuplicate] = []

app = FastAPI()


@app.get("/tickets/", response_model=list[TicketResponse])
async def get_tickets(status: Literal["open", "resolved", "closed"] | None = None, 
                        db: AsyncSession = Depends(get_db)):
                
    query = select(Ticket).order_by(Ticket.created_at.desc())
    if status:
        query = query.where(Ticket.status == status)
    result = await db.execute(query)
    tickets = result.scalars().all()
    return tickets


@app.get("/tickets/{ticket_id}")
async def get_ticket(ticket_id: int):
    pass


@app.post("/tickets/", response_model=TicketResponse, status_code=201)
async def create_ticket(body: TicketCreate, db: AsyncSession = Depends(get_db)):
    ticket = Ticket(
        text=body.text,
        category="unknown",
        priority="unknown",
    )
    db.add(ticket)
    await db.commit()
    await db.refresh(ticket)

    classify_ticket_task.delay(ticket.id, body.text)
    return ticket


@app.patch("/tickets/{ticket_id}/status")
async def update_ticket_status(ticket_id: int, body: TicketStatusUpdate, db: AsyncSession = Depends(get_db)):
    ticket = await db.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    if body.status not in ALLOWED_TRANSITIONS[ticket.status]:
        raise HTTPException(status_code=400, detail="Invalid status transition")
    ticket.status = body.status
    await db.commit()
    await db.refresh(ticket)

    return ticket


@app.delete("/tickets/{ticket_id}")
async def delete_ticket(ticket_id: int):
    ticket = await db.get(Ticket, ticket_id)

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if ticket.status == "closed":
        raise HTTPException(status_code=400, detail="Ticket is already closed")

    ticket.status = "closed"
    await db.commit()
    await db.refresh(ticket)

    duplicates = await find_similar_open_tickets(
        ticket_id=ticket.id,
        embedding=ticket.embedding_vector,
        category=ticket.category,
        db=db,
    )


    return TicketCloseResponse(
        ticket=ticket,
        status="closed",
        suggested_duplicates=duplicates,
    )

