import asyncio

from celery import Celery

from app.settings import settings

celery = Celery("issuetracker", broker=settings.CELERY_BROKER_URL)


@celery.task
def classify_ticket_task(ticket_id: int, text: str):
    asyncio.run(_classify_ticket(ticket_id, text))


async def _classify_ticket(ticket_id: int, text: str):
    from app.database.database import async_session
    from app.models.models import Ticket
    from app.services.classifier import classify

    async with async_session() as db:
        prediction = await classify(text, db)

        ticket = await db.get(Ticket, ticket_id)
        
        ticket.category = prediction["category"]
        ticket.priority = prediction["priority"]
        ticket.embedding_vector = prediction["vector"]
        await db.commit()
