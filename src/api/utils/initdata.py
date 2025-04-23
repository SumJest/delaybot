import hashlib
import hmac
import urllib.parse

from fastapi import HTTPException
from starlette.status import HTTP_401_UNAUTHORIZED


def parse_init_data(init_data: str) -> dict:
    return dict(urllib.parse.parse_qsl(init_data))

def validate_telegram_init_data(init_data: str, bot_token: str) -> dict:
    try:
        data = parse_init_data(init_data)
        hash_received = data.pop("hash")
    except Exception:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Invalid init data")

    # Собираем строку в правильном порядке
    data_check_string = "\n".join(
        f"{k}={v}" for k, v in sorted(data.items())
    )

    secret_key = hashlib.sha256(bot_token.encode()).digest()
    calculated_hash = hmac.new(
        key=secret_key,
        msg=data_check_string.encode(),
        digestmod=hashlib.sha256
    ).hexdigest()

    if calculated_hash != hash_received:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Invalid hash")

    return data