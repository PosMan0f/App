LAST_MESSAGE_PREVIEW_LIMIT = 60


def truncate(text, limit):
    if text is None:
        return ''
    text = str(text)
    if len(text) <= limit:
        return text
    if limit <= 3:
        return '.' * limit
    return f"{text[:limit - 3]}..."