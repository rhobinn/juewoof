from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from fastapi.responses import HTMLResponse

global_router = APIRouter()

global_templates = Jinja2Templates(directory="routers/global_/templates")


### Stripe

from config.credentials import STRIPE_SECRET_KEY
import stripe

stripe.api_key = STRIPE_SECRET_KEY

@global_router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    is_authenticated = False
    return global_templates.TemplateResponse("index.html", {"request": request, "is_authenticated": is_authenticated})
