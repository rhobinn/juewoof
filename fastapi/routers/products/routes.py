from fastapi import APIRouter, Request, Depends, Body, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlmodel import Session, select
from main import get_session
import uuid 
from utils.crud import create_entity, update_entity, get_create_view, get_read_view, get_update_view, deactivate_entity, activate_entity, get_all_entities
from core.auth import get_current_user

from database.models import ProductCreate, Product

products_router = APIRouter()

products_templates = Jinja2Templates(directory=["routers/global_/templates", "routers/products/templates"])

### CREATE | GET : WEBVIEW - Creation of product
@products_router.get("/create", response_class=HTMLResponse)
async def create_product_form(  request: Request,
                                user: dict = Depends(get_current_user)
                              ):

    hero_title="Agregar producto"
    return products_templates.TemplateResponse("products_create.html", {"request": request,  "hero_title":hero_title, "user": user})

@products_router.get("/create", response_class=HTMLResponse)
async def create_product_form(  request: Request,
                                user: dict = Depends(get_current_user)
                              ):

    fields_with_options = []

    return get_create_view(
        request=request,
        templates=products_templates, 
        template_name="products_create.html",
        fields_with_options=fields_with_options,
        hero_title="Agregar producto",
        hero_subtitle="",
        user=user,
    )

### CREATE | POST - Creation of a product
@products_router.post("/create")
async def create_product(   request: Request, 
                        entity_data: ProductCreate = Body(...), 
                        db: Session = Depends(get_session)
                        ):  
    
    return create_entity(
        request=request, 
        entity_data=entity_data, 
        EntityClass=Product, 
        db=db
    )


### READ | GET: WEBVIEW- View info of a single dog
@products_router.get("/{entity_uuid}")
async def get_product(  request: Request, 
                        entity_uuid: uuid.UUID, 
                        db: Session = Depends(get_session),
                        user: dict = Depends(get_current_user)
                    ):

    return get_read_view(
        request=request,
        templates=products_templates,
        entity_uuid=entity_uuid,
        EntityClass=Product,
        db=db,
        template_name="products_read.html",
        hero_title="Información del producto",
        hero_subtitle="",
        user=user
    )


### UPDATE | POST - update info of a product 
@products_router.patch("/update/{entity_uuid}")
async def update_product(   request: Request, 
                            entity_uuid: uuid.UUID, 
                            entity_data: ProductCreate = Body(...), 
                            db: Session = Depends(get_session)
                        ):  
    return update_entity(
        request=request, 
        entity_uuid=entity_uuid, 
        entity_data=entity_data, 
        db=db, 
        EntityClass=Product
    )


### UPDATE | GET: WEBVIEW - update info of a product 
@products_router.get("/update/{entity_uuid}")
async def update_product_form(  request: Request,
                                entity_uuid: uuid.UUID, 
                                db: Session = Depends(get_session),
                                user: dict = Depends(get_current_user)
                            ):

    return get_update_view(
        request=request,
        templates=products_templates,
        entity_uuid=entity_uuid,
        EntityClass=Product,
        fields_with_options=[],
        extra_fields=[],
        template_name="products_update.html",
        hero_title="Actualizar",
        hero_subtitle="Actualiza los detalles del producto",
        user=user,
        db=db,
    )


### DEACTIVATE | PATCH - Deactivate a product
@products_router.patch("/deactivate/{entity_uuid}")
async def deactivate_product(request: Request, entity_uuid: uuid.UUID, db: Session = Depends(get_session)):
    return deactivate_entity(   request=request,
                                entity_uuid=entity_uuid,
                                EntityClass=Product,
                                db=db, 
                            )
### ACTIVATE | PATCH - Deactivate a product
@products_router.patch("/activate/{entity_uuid}")
async def activate_product(request: Request, entity_uuid: uuid.UUID, db: Session = Depends(get_session)):
    return activate_entity(   request=request,
                                entity_uuid=entity_uuid,
                                EntityClass=Product,
                                db=db, 
                            )

from sqlalchemy.orm import selectinload
### INDEX(ALL)| GET : WEBVIEW  View info of all product 
@products_router.get("/index/all", response_class=HTMLResponse)  
async def get_all_products( request: Request,
                            db: Session = Depends(get_session),
                            user: dict = Depends(get_current_user),
                           ):
    return await get_all_entities(  request=request,
                                    templates=products_templates,
                                    db=db,
                                    EntityClass=Product,
                                    template_name="Products_index.html", enum_fields=None,
                                    extra_db_fields=None, 
                                    hero_title=None,
                                    hero_subtitle=None,
                                    user=user
                                )
