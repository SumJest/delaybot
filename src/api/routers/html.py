from fastapi import APIRouter
from starlette.requests import Request
from starlette.responses import HTMLResponse

from api.application import templates

router = APIRouter(tags=['html'])


@router.get('/webapp', response_class=HTMLResponse)
async def webapp_page(request: Request):
    return templates.TemplateResponse('simple.html', {'request': request})
