from collections import Counter

from sentence_transformers import SentenceTransformer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Ticket
from app.settings import settings

model = SentenceTransformer(settings.MODEL_NAME)

K_NEIGHBORS = 3



async def classify(text: str, db: AsyncSession) -> dict:
    vector = model.encode(text).tolist()

    query = (
        select(Ticket.category, Ticket.priority)
        .order_by(Ticket.embedding_vector.cosine_distance(vector))
        .limit(K_NEIGHBORS)
    )
    result = await db.execute(query)
    neighbors = result.all()

    if not neighbors:
        return {"category": "unknown", "priority": "unknown", "vector": vector}

    category = Counter(n.category for n in neighbors).most_common(1)[0][0]
    priority = Counter(n.priority for n in neighbors).most_common(1)[0][0]
    return {"category": category, "priority": priority, "vector": vector}
