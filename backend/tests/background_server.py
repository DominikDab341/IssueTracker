"""Subprocess fixture: real Uvicorn/lifespan/BackgroundTasks, isolated test DB only."""
import sys
import time

from tests.support import TEST_URL
from app.services import classifier
from app.api.main import app
import uvicorn


def encode(description):
    if sys.argv[2] == "slow":
        time.sleep(120)
    return [1.0] + [0.0] * 383


if __name__ == "__main__":
    classifier.encode_text = encode
    uvicorn.run(app, host="127.0.0.1", port=int(sys.argv[1]), log_level="error")
