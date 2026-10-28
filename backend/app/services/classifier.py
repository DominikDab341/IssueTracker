from collections import Counter
from threading import Lock

import anyio

from sentence_transformers import SentenceTransformer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain import ClassificationPrediction, Priority
from app.models.models import ClassificationReference, Ticket
from app.settings import settings
from app.ticket_status import ACTIVE_STATUSES
from app.services.access import available_tickets

# Model ładowany przy pierwszej klasyfikacji, w wątku poza pętlą żądań API.
_model: SentenceTransformer | None = None
_model_lock = Lock()


def get_model() -> SentenceTransformer:
    global _model
    with _model_lock:
        if _model is None:
            _model = SentenceTransformer(settings.MODEL_NAME)
    return _model


def encode_text(text: str) -> list[float]:
    model = get_model()
    with _model_lock:
        return model.encode(text).tolist()

K_NEIGHBORS = 3

DUPLICATE_THRESHOLD = 0.25  
MAX_SUGGESTIONS = 5

async def classify(text: str, db: AsyncSession) -> ClassificationPrediction:
    vector = await anyio.to_thread.run_sync(encode_text, text)
    distance = ClassificationReference.embedding_vector.cosine_distance(vector)
    
    knn_query = (
        select(ClassificationReference.category, ClassificationReference.base_priority)
        .order_by(distance, ClassificationReference.id)
        .limit(K_NEIGHBORS)
    )
    
    knn_result = await db.execute(knn_query)
    neighbors = knn_result.all()

    if not neighbors:
        return ClassificationPrediction(category="unknown", base_priority=None, automatic_priority=None, vector=vector)

    category = Counter(n.category for n in neighbors).most_common(1)[0][0]
    base_priority = Priority(Counter(n.base_priority for n in neighbors).most_common(1)[0][0])

    return ClassificationPrediction(category=category, base_priority=base_priority, automatic_priority=base_priority, vector=vector)



async def find_similar_open_tickets(
    ticket_id: int, embedding: list[float] | None, category: str, db: AsyncSession, *, actor
) -> list[dict]:
    if embedding is None:
        return []
    distance = Ticket.embedding_vector.cosine_distance(embedding)
    
    result = await db.execute(
        select(Ticket.id, Ticket.text, distance.label("distance"))
        .where(
            Ticket.status.in_(ACTIVE_STATUSES),
            available_tickets(actor),
            Ticket.embedding_version == Ticket.content_version,
            Ticket.category == category,
            Ticket.id != ticket_id,
            distance < DUPLICATE_THRESHOLD,
        )
        .order_by(distance)
        .limit(MAX_SUGGESTIONS)
    )
    
    return [
        {"id": row.id, "text": row.text, "similarity": round(1 - row.distance, 3)}
        for row in result.all()
    ]
