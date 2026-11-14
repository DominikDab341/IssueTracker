from functools import lru_cache

from transformers import AutoTokenizer

from app.settings import settings


# sentence_bert_config.json modelu all-MiniLM-L6-v2: max_seq_length=256.
# Limit obejmuje tokeny specjalne; tokenizer BERT sam podaje 512.
MAX_INPUT_TOKENS = 256
MAX_TEXT_CHARACTERS = 10000


class TokenizerUnavailableError(RuntimeError):
    pass


@lru_cache(maxsize=1)
def get_tokenizer():
    model_name = settings.MODEL_NAME
    if model_name == "all-MiniLM-L6-v2":
        model_name = "sentence-transformers/all-MiniLM-L6-v2"
    try:
        return AutoTokenizer.from_pretrained(model_name)
    except OSError as exc:
        raise TokenizerUnavailableError("The model tokenizer is unavailable. Try again later.") from exc


def normalize_ticket_text(value: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError("The ticket description is required.")
    if len(value) > MAX_TEXT_CHARACTERS:
        raise ValueError(f"The ticket description can contain at most {MAX_TEXT_CHARACTERS} characters.")
    return value


def validate_ticket_text(value: str) -> str:
    value = normalize_ticket_text(value)
    tokens = get_tokenizer().encode(value, add_special_tokens=True, truncation=False)
    if len(tokens) > MAX_INPUT_TOKENS:
        raise ValueError(
            f"The ticket description has {len(tokens)} tokens. "
            f"The all-MiniLM-L6-v2 limit is {MAX_INPUT_TOKENS} tokens. Shorten the description."
        )
    return value
