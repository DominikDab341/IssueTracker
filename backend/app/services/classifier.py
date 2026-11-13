from collections import Counter
from threading import Lock
import hashlib
import json

import anyio

from sentence_transformers import SentenceTransformer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain import Category, ClassificationPrediction
from app.services.priority_classifier import predict_priority_details
from app.services.priority_information import POLICY_VERSION, needs_priority_information
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
            _model = SentenceTransformer(settings.MODEL_NAME, revision=settings.MODEL_REVISION)
    return _model


def encode_text(text: str) -> list[float]:
    model = get_model()
    with _model_lock:
        return model.encode(text).tolist()

APPROVED_TICKET_SOURCE = "approved_ticket"


def active_reference_filter():
    return (ClassificationReference.source.in_([settings.CLASSIFICATION_REFERENCE_SOURCE, APPROVED_TICKET_SOURCE])
            & ClassificationReference.category.in_(list(Category)))

async def classify(text: str, db: AsyncSession) -> ClassificationPrediction:
    vector = await anyio.to_thread.run_sync(encode_text, text)
    distance = ClassificationReference.embedding_vector.cosine_distance(vector)
    
    knn_query = (
        select(ClassificationReference.source_key, ClassificationReference.text,
               ClassificationReference.source, ClassificationReference.category, ClassificationReference.base_priority,
               distance.label("distance"))
        .where(active_reference_filter())
        .order_by(distance, ClassificationReference.id)
    )
    
    knn_result = await db.execute(knn_query)
    references = knn_result.mappings().all()
    neighbors = references[:settings.K_NEIGHBORS]

    if not neighbors:
        return ClassificationPrediction(category="unknown", base_priority=None, automatic_priority=None, vector=vector,
                                        category_review_reason="no_references", priority_review_reason="no_references")

    category = Counter(n["category"] for n in neighbors).most_common(1)[0][0]
    supporters = [row for row in neighbors if row["category"] == category]
    category_score = max(-1.0, min(1.0, max(1 - float(row["distance"]) for row in supporters)))
    vote_share = len(supporters) / len(neighbors)
    category_reason = ("low_category_similarity" if category_score < settings.CATEGORY_MIN_SIMILARITY else
                       "split_category_vote" if vote_share < settings.CATEGORY_MIN_VOTE_SHARE else None)
    # Distance depends on the query and must never be part of the training cache key.
    references = sorted([{key: value for key, value in row.items() if key != "distance"} for row in references],
                        key=lambda row: (row["source"], row["source_key"]))
    priority = await anyio.to_thread.run_sync(
        lambda: predict_priority_details(text, references,
                                 source=settings.CLASSIFICATION_REFERENCE_SOURCE,
                                 model_name=settings.MODEL_NAME, model_revision=settings.MODEL_REVISION))
    priority_reason = ("no_known_priority_terms" if not priority.has_known_terms else
                       "low_priority_score" if priority.score < settings.PRIORITY_MIN_SCORE else None)
    if priority_reason is None and needs_priority_information(text):
        priority_reason = "sparse_priority_information"
    accepted_priority = None if priority_reason else priority.label
    policy = {"training": priority.version, "k": settings.K_NEIGHBORS,
              "priority_information_policy": POLICY_VERSION,
              "category_min_similarity": settings.CATEGORY_MIN_SIMILARITY,
              "category_min_vote_share": settings.CATEGORY_MIN_VOTE_SHARE,
              "priority_min_score": settings.PRIORITY_MIN_SCORE,
              "escalation": [settings.ESCALATION_ENABLED, settings.ESCALATION_MIN_USERS,
                             settings.ESCALATION_WINDOW_HOURS, settings.ESCALATION_MIN_SIMILARITY]}
    version = "helpdesk-v2:" + hashlib.sha256(json.dumps(policy, sort_keys=True).encode()).hexdigest()
    return ClassificationPrediction(category="unknown" if category_reason else category,
                                    base_priority=accepted_priority, automatic_priority=accepted_priority,
                                    vector=vector, classification_version=version,
                                    predicted_category=category, predicted_base_priority=priority.label,
                                    category_score=category_score, priority_score=priority.score,
                                    category_review_reason=category_reason, priority_review_reason=priority_reason)



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
            Ticket.id != ticket_id,
            distance < 1 - settings.DUPLICATE_MIN_SIMILARITY,
            *([Ticket.category == category] if settings.DUPLICATE_SAME_CATEGORY else []),
        )
        .order_by(distance)
        .limit(settings.MAX_DUPLICATE_SUGGESTIONS)
    )
    
    return [
        {"id": row.id, "text": row.text, "similarity": round(1 - row.distance, 3)}
        for row in result.all()
    ]
