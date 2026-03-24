MAX_INPUT_LENGTH = 10_000


def validate_input(text: str, max_length: int) -> str:
    """
    Validates and sanitizes text input.
    Handles None, non-string types, and length truncation.
    """
    if text is None:
        return ""
    if not isinstance(text, str):
        text = str(text)
    if len(text) > max_length:
        return text[:max_length]
    return text
