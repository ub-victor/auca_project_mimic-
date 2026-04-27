import re
import string

# Punctuation minus hyphen (keep "open-source") and keep alphanumeric tokens intact
_PUNCT = string.punctuation.replace("-", "")


def clean(text: str) -> str:
    text = text.lower()
    # Remove punctuation but preserve alphanumeric tokens like "3nf", "ipv4", "o(log"
    text = re.sub(r"[^\w\s-]", " ", text)
    # Collapse hyphens/underscores to space so "open-source" → "open source"
    text = re.sub(r"[-_]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()
