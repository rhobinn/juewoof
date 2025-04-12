from fastapi import APIRouter, Request, Depends, Body
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlmodel import Session
from main import get_session
from core.auth import get_current_user
from sqlmodel import select

from database.models import User
from fastapi import HTTPException

reservations_router = APIRouter()

reservations_templates = Jinja2Templates(directory=["routers/global_/templates", "routers/reservations/templates"])

@reservations_router.get("/daypass", response_class=HTMLResponse)
async def reserve_daypass(  request: Request,
                            db: Session = Depends(get_session), 
                            user: dict = Depends(get_current_user)
                            ):

    from main import app

    statement = select(User).where(User.id == user['id'])
    tutor = db.exec(statement).one_or_none()

    if tutor is None:
        raise HTTPException(status_code=404, detail="Tutor not found")

    active_dogs = [dog for dog in tutor.dogs if dog.is_active]
    return reservations_templates.TemplateResponse("daypass.html", {"request": request, 
                                                                    "entities_data":active_dogs,  
                                                                    "user": user
                                                                    })

from fastapi.responses import JSONResponse
import random
@reservations_router.get("/daypass-available-dates", name="get_daypass_available_dates")
async def get_daypass_available_dates():
    # Ideally fetch these from your DB or business logic
    enabled_dates = [
        "11-04-25",
        "12-04-25",
        "13-04-25",
        f"{random.randint(1, 9)}-04-25",
    ]
    return JSONResponse(content=enabled_dates)