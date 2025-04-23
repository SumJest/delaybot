from fastapi import Header, Depends, Security, HTTPException
from fastapi.security.api_key import APIKeyHeader
from starlette import status
from api.dependencies import get_services
from api.utils.initdata import validate_telegram_init_data
from containers import ServicesContainer

# Для явного отображения в Swagger
init_data_header = APIKeyHeader(name="X-Telegram-InitData", auto_error=False)


async def auth_initdata_user(
        x_telegram_initdata: str = Security(init_data_header),
        services_container: ServicesContainer = Depends(get_services),
):
    if not x_telegram_initdata:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Telegram init data")
    data = validate_telegram_init_data(x_telegram_initdata, bot_token=services_container.bot.token)

    user_service = services_container.user_service
    user_model = await user_service.to_model(data['user'])
    user = await user_service.upsert(user_model, item_id=data['user']['id'], auto_commit=True, auto_refresh=True)
    if user.is_blocked:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Your account is blocked")
    return user
