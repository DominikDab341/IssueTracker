"""Small in-memory TF-IDF model, rebuilt when approved references change."""
import hashlib
import json
from threading import Lock

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline

from app.domain import Priority

_lock = Lock()
_cached_version = None
_cached_model = None


def make_priority_model():
    # Same parameters and preprocessing as the evaluated EN candidate.
    return make_pipeline(TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True),
                         LogisticRegression(C=100, max_iter=2000, random_state=20261107))


def predict_priority(text, references, *, source, model_name, model_revision):
    global _cached_model, _cached_version
    payload = {"method": "helpdesk-v1-tfidf-logreg-c100", "category_k": 3,
               "source": source, "embedding_model": model_name, "embedding_revision": model_revision,
               "references": references}
    version = "helpdesk-v1:" + hashlib.sha256(json.dumps(payload, ensure_ascii=False,
                                                        sort_keys=True).encode("utf-8")).hexdigest()
    if not references:
        return None, version
    labels = [row["base_priority"] for row in references]
    # A partially populated reference set can contain only one class.
    if len(set(labels)) == 1:
        return Priority(labels[0]), version
    with _lock:
        if version != _cached_version:
            model = make_priority_model()
            model.fit([row["text"] for row in references], labels)
            _cached_model, _cached_version = model, version
        return Priority(_cached_model.predict([text])[0]), version
