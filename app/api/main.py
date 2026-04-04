from datetime import datetime

from fastapi import Depends, FastAPI
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_db
from app.models.models import Ticket
from app.celery_app import classify_ticket_task


class TicketCreate(BaseModel):
    text: str


class TicketResponse(BaseModel):
    id: int
    text: str
    category: str
    priority: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


app = FastAPI()


@app.get("/tickets/", response_model=list[TicketResponse])
async def get_tickets(db: AsyncSession = Depends(get_db)):
    query = select(Ticket).order_by(Ticket.created_at.desc())
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


@app.delete("/tickets/{ticket_id}")
async def delete_ticket(ticket_id: int):
    return {"message": "Ticket deleted successfully"}

