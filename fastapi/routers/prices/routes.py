from fastapi import APIRouter, Request, Depends, Body, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlmodel import Session, select
from main import get_session
import uuid 
from utils.crud import create_entity, update_entity, get_create_view, get_read_view, get_update_view, deactivate_entity, activate_entity, get_all_entities
from core.auth import get_current_user

from database.models import PriceCreate, Price

prices_router = APIRouter()

prices_templates = Jinja2Templates(directory=["routers/global_/templates", "routers/prices/templates"])

### CREATE | GET : WEBVIEW - Creation of price
@prices_router.get("/create/{entity_uuid}", response_class=HTMLResponse)
async def create_price_form(    request: Request,
                                entity_uuid: uuid.UUID, 
                                user: dict = Depends(get_current_user)
                            ):

    return get_create_view(
        request=request,
        templates=prices_templates, 
        template_name="prices_create.html",
        fields_with_options=['pricing_type'],
        hero_title="Agregar precio",
        hero_subtitle="",
        user=user,
        **{"product_id":entity_uuid}
    )


### CREATE | POST - Creation of a price
@prices_router.post("/create")
async def create_price( request: Request, 
                        entity_data: PriceCreate = Body(...), 
                        db: Session = Depends(get_session),
                        ):  
    
    return create_entity(
        request=request, 
        entity_data=entity_data, 
        EntityClass=Price, 
        db=db,
    )


### READ | GET: WEBVIEW- View info of a single dog
@prices_router.get("/{entity_uuid}")
async def get_price(  request: Request, 
                        entity_uuid: uuid.UUID, 
                        db: Session = Depends(get_session),
                        user: dict = Depends(get_current_user)
                    ):

    return get_read_view(
        request=request,
        templates=prices_templates,
        entity_uuid=entity_uuid,
        EntityClass=Price,
        db=db,
        template_name="prices_read.html",
        hero_title="Información del precio",
        hero_subtitle="",
        user=user
    )


### UPDATE | POST - update info of a price 
@prices_router.patch("/update/{entity_uuid}")
async def update_price(   request: Request, 
                            entity_uuid: uuid.UUID, 
                            entity_data: PriceCreate = Body(...), 
                            db: Session = Depends(get_session)
                        ):  
    return update_entity(
        request=request, 
        entity_uuid=entity_uuid, 
        entity_data=entity_data, 
        db=db, 
        EntityClass=Price
    )


### UPDATE | GET: WEBVIEW - update info of a price 
@prices_router.get("/update/{entity_uuid}")
async def update_price_form(  request: Request,
                                entity_uuid: uuid.UUID, 
                                db: Session = Depends(get_session),
                                user: dict = Depends(get_current_user)
                            ):

    return get_update_view(
        request=request,
        templates=prices_templates,
        entity_uuid=entity_uuid,
        EntityClass=Price,
        fields_with_options=[],
        extra_fields=[],
        template_name="prices_update.html",
        hero_title="Actualizar",
        hero_subtitle="Actualiza los detalles del precio",
        user=user,
        db=db,
    )


### DEACTIVATE | PATCH - Deactivate a price
@prices_router.patch("/deactivate/{entity_uuid}")
async def deactivate_price(request: Request, entity_uuid: uuid.UUID, db: Session = Depends(get_session)):
    return deactivate_entity(   request=request,
                                entity_uuid=entity_uuid,
                                EntityClass=Price,
                                db=db, 
                            )
### ACTIVATE | PATCH - Deactivate a price
@prices_router.patch("/activate/{entity_uuid}")
async def activate_price(request: Request, entity_uuid: uuid.UUID, db: Session = Depends(get_session)):
    return activate_entity(   request=request,
                                entity_uuid=entity_uuid,
                                EntityClass=Price,
                                db=db, 
                            )

from sqlalchemy.orm import selectinload
### INDEX(ALL)| GET : WEBVIEW  View info of all price 
@prices_router.get("/index/all", response_class=HTMLResponse)  
async def get_all_prices( request: Request,
                            db: Session = Depends(get_session),
                            user: dict = Depends(get_current_user),
                           ):
    return await get_all_entities(  request=request,
                                    templates=prices_templates,
                                    db=db,
                                    EntityClass=Price,
                                    template_name="Prices_index.html", enum_fields=None,
                                    extra_db_fields=None, 
                                    hero_title=None,
                                    hero_subtitle=None,
                                    user=user
                                )
