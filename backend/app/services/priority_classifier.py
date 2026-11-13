"""Small in-memory TF-IDF model, rebuilt when approved references change."""
import hashlib
import json
from dataclasses import dataclass
from threading import Lock

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline

from app.domain import Priority

# Critical incidents are underrepresented in the pilot references and costlier to miss.
_CLASS_WEIGHTS = {priority.value: 3.0 if priority == Priority.CRITICAL else 1.0 for priority in Priority}

_lock = Lock()
_cached_version = None
_cached_model = None


def make_priority_model():
    return make_pipeline(TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True),
                         LogisticRegression(C=100, max_iter=2000, random_state=20261107,
                                            class_weight=_CLASS_WEIGHTS.copy()))


@dataclass(frozen=True)
class PriorityPrediction:
    label: Priority | None
    score: float | None
    version: str
    has_known_terms: bool


def predict_priority_details(text, references, *, source, model_name, model_revision):
    global _cached_model, _cached_version
    payload = {"method": "helpdesk-v1-tfidf-logreg-c100", "class_weight": _CLASS_WEIGHTS, "category_k": 3,
               "source": source, "embedding_model": model_name, "embedding_revision": model_revision,
               "references": references}
    version = "helpdesk-v1:" + hashlib.sha256(json.dumps(payload, ensure_ascii=False,
                                                        sort_keys=True).encode("utf-8")).hexdigest()
    if not references:
        return PriorityPrediction(None, None, version, False)
    labels = [row["base_priority"] for row in references]
    # A partially populated reference set can contain only one class.
    if len(set(labels)) == 1:
        return PriorityPrediction(Priority(labels[0]), 1.0, version, True)
    with _lock:
        if version != _cached_version:
            model = make_priority_model()
            model.fit([row["text"] for row in references], labels)
            _cached_model, _cached_version = model, version
        terms = _cached_model.steps[0][1].transform([text])
        probabilities = _cached_model.predict_proba([text])[0]
        winner = int(probabilities.argmax())
        return PriorityPrediction(Priority(_cached_model.classes_[winner]), float(probabilities[winner]), version, terms.nnz > 0)


def predict_priority(text, references, **options):
    result = predict_priority_details(text, references, **options)
    return result.label, result.version
