from fastapi import APIRouter, Depends
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from fastapi.responses import HTMLResponse
from core.auth import get_current_user
global_router = APIRouter()

global_templates = Jinja2Templates(directory="routers/global_/templates")


@global_router.get("/", response_class=HTMLResponse)
async def index(request: Request, user: dict = Depends(get_current_user)):
    return global_templates.TemplateResponse("index.html", {"request": request, "user":user})
