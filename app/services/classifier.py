from collections import Counter

from sentence_transformers import SentenceTransformer
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Ticket
from app.settings import settings

model = SentenceTransformer(settings.MODEL_NAME)

K_NEIGHBORS = 3
SIMILARITY_THRESHOLD = 0.4
PRIORITY_SCALE = ["low", "medium", "high", "critical"]
ESCALATION_CATEGORIES = {"bug", "performance"}


async def classify(text: str, db: AsyncSession) -> dict:
    vector = model.encode(text).tolist()
    distance = Ticket.embedding_vector.cosine_distance(vector)

    knn_query = (
        select(Ticket.category, Ticket.priority)
        .order_by(distance)
        .limit(K_NEIGHBORS)
    )
    
    knn_result = await db.execute(knn_query)
    neighbors = knn_result.all()

    if not neighbors:
        return {"category": "unknown", "priority": "unknown", "vector": vector}

    category = Counter(n.category for n in neighbors).most_common(1)[0][0]
    priority = Counter(n.priority for n in neighbors).most_common(1)[0][0]

    if category in ESCALATION_CATEGORIES:
        priority = await escalate_priority(priority, category, distance, db)

    return {"category": category, "priority": priority, "vector": vector}


async def escalate_priority(base_priority: str, category: str, distance, db: AsyncSession) -> str:
    similar_count = await db.scalar(
        select(func.count()).select_from(Ticket).where(
            distance < SIMILARITY_THRESHOLD,
            Ticket.category == category,
        )
    )
    total_count = await db.scalar(
        select(func.count()).select_from(Ticket).where(
            Ticket.category == category,
        )
    )

    if total_count == 0:
        return base_priority

    percent = similar_count / total_count * 100

    if percent >= 35:
        return "critical"

    if base_priority in PRIORITY_SCALE:
        idx = PRIORITY_SCALE.index(base_priority)
    else:
        idx = 0

    if percent >= 25:
        idx += 2
    elif percent >= 10:
        idx += 1

    return PRIORITY_SCALE[min(idx, len(PRIORITY_SCALE) - 1)]
