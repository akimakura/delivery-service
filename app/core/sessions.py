import secrets
from fastapi import Request


def get_or_create_session_id(request: Request) -> str:  
    """
    Получаем session_id из заголовка X-Session-Id, если он есть, иначе генерируем случайный UUID
    """
    sid = request.headers.get("X-Session-Id")
    if sid and isinstance(sid, str) and sid.strip():
        return sid.strip()
    return request.client.host if request.client else "anonymous"
