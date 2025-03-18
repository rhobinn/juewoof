from fastapi import HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select
from db.models import IdempotencyKey
from typing import Type
from sqlmodel import SQLModel
import uuid
from enum import Enum
from fastapi.templating import Jinja2Templates
from utils.forms import generate_options_dict, handle_idempotency_key

def get_create_view(
        *,
        request: Request,
        templates: Jinja2Templates,
        fields_with_options: list,
        template_name: str,
        hero_title: str = "",
        hero_subtitle: str = "", 
    ):


    # Create select_options_dict dynamically
    select_options_dict = generate_options_dict(fields_with_options)

    return templates.TemplateResponse(
        template_name,
        {
            "request": request,
            "select_options_dict": select_options_dict,
            "hero_title": hero_title,
            "hero_subtitle": hero_subtitle,
        },
    )

def get_update_view(
        *,
        request: Request,
        templates: Jinja2Templates,
        entity_uuid: uuid.UUID,
        EntityClass: Type[SQLModel],   # The SQLModel database model class representing the target database table (e.g., Dog).
        fields_with_options: list,
        extra_fields: dict = None,  # Now default to None, but can be passed as a dictionary
        template_name: str,
        hero_title: str = "",
        hero_subtitle: str = "", 
        db: Session, 
    ):

    statement = select(EntityClass).where(EntityClass.id == entity_uuid)
    entity = db.exec(statement).one_or_none()

    if entity is None:
        raise HTTPException(status_code=404, detail=f"{EntityClass.__translated_name__} no encontrado")    

    entity_dict = entity.model_dump()  

    # Filter out empty fields and handle Enums
    entity_data = {
        key: value.value if isinstance(value, Enum) else value
        for key, value in entity_dict.items() if value
    }

    #Add extra fields to entity data if provided
    if extra_fields:
        for field  in extra_fields:
            entity_data[field] = getattr(entity, field, None)

    # Create select_options_dict dynamically
    select_options_dict = generate_options_dict(fields_with_options)

    return templates.TemplateResponse(
        template_name,
        {
            "request": request,
            "entity_data": entity_data,
            "select_options_dict": select_options_dict,
            "hero_title": hero_title,
            "hero_subtitle": hero_subtitle,
        },
    )


def create_entity(
    *,
    request: Request,
    entity_data: SQLModel,         # The input data for the new entity. Can be any SQLModel subclass (e.g., DogCreate).
    EntityClass: Type[SQLModel],   # The SQLModel database model class representing the target database table (e.g., Dog).
    db: Session, 
    extra_fields: dict = None
):
    """Handles entity creation with idempotency, database commit, and redirect response."""

    idempotency_key = request.headers.get("Idempotency-Key")
    if not idempotency_key:
        raise HTTPException(status_code=400, detail="Idempotency-Key header is required")

    redirect_response = handle_idempotency_key(db, idempotency_key, request)
    if redirect_response:
        return redirect_response  

    try:
        # Merge extra fields if provided (e.g., tutor_id for Dog)
        entity_data_dict = entity_data.model_dump()
        if extra_fields:
            entity_data_dict.update(extra_fields)

        entity = EntityClass(**entity_data_dict)

        db.add(entity)
        db.commit()
        db.refresh(entity)

        # Store idempotency key
        new_idempotency_key = IdempotencyKey(
            key=idempotency_key,
            created_object_id=entity.id,
            created_object_type=EntityClass.__name__
        )
        db.add(new_idempotency_key)
        db.commit()

        # Generate redirect URL
        redirect_url = request.url_for(f"get_{EntityClass.__tablename__}", entity_uuid=entity.id)
        return RedirectResponse(url=redirect_url, status_code=303)

    except Exception as e:
        db.rollback()  # Rollback in case of an error
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")



def get_read_view(
    *,
    request: Request,
    templates: Jinja2Templates,
    entity_uuid: uuid.UUID,
    EntityClass: Type[SQLModel],   # The SQLModel database model class representing the target database table (e.g., Dog).
    db: Session,
    template_name: str,
    hero_title: str = "",
    hero_subtitle: str = "",
    extra_fields: dict = None  # Now default to None, but can be passed as a dictionary
):
    """Fetches entity data and renders it using the specified template."""

    # Query the database for the entity
    statement = select(EntityClass).where(EntityClass.id == entity_uuid)
    entity = db.exec(statement).one_or_none()

    if entity is None:
        raise HTTPException(status_code=404, detail=f"{EntityClass.__translated_name__} no encontrado")

    entity_dict = entity.model_dump()

    # Filter out empty fields and handle Enums
    entity_data = {
        key: value.value if isinstance(value, Enum) else value
        for key, value in entity_dict.items() if value
    }

    #Add extra fields to entity data if provided
    if extra_fields:
        for field  in extra_fields:
            entity_data[field] = getattr(entity, field, None)

    return templates.TemplateResponse(
        template_name,
        {
            "request": request,
            "entity_data": entity_data,
            "hero_title": hero_title,
            "hero_subtitle": hero_subtitle,
        },
    )


def update_entity(
    *,
    request: Request,
    entity_uuid: uuid.UUID,
    entity_data: SQLModel,         # The input data for the new entity. Can be any SQLModel subclass (e.g., DogCreate).
    EntityClass: Type[SQLModel],   # The SQLModel database model class representing the target database table (e.g., Dog).
    db: Session,
):
    # Fetch the entity from the database
    entity = db.exec(select(EntityClass).where(EntityClass.id == entity_uuid)).one_or_none()
    
    if not entity:
        raise HTTPException(status_code=404, detail=f"{EntityClass.__name__} no encontrado")
    
    # Update entity fields based on the provided data
    for key, value in entity_data.model_dump().items():
        setattr(entity, key, value)

    # Commit the changes to the database
    db.commit()

    # Redirect to the view page for the updated entity
    redirect_url = request.url_for(f"get_{EntityClass.__tablename__}", entity_uuid=entity_uuid)
    return RedirectResponse(url=redirect_url, status_code=303)

def deactivate_entity(
    *,
    request: Request, 
    entity_uuid: uuid.UUID, 
    EntityClass: Type[SQLModel],
    db: Session, 
):
    entity = db.exec(select(EntityClass).where(EntityClass.id == entity_uuid)).one_or_none()

    if not entity:
        raise HTTPException(status_code=404, detail=f"{EntityClass.__translated_name__} no encontrado")

    setattr(entity, "is_active", False)
    db.commit()

    redirect_url = request.url_for(f"get_all_{EntityClass.__tablename__}s")
    return RedirectResponse(url=redirect_url, status_code=303)


def activate_entity(
    *,
    request: Request, 
    entity_uuid: uuid.UUID, 
    EntityClass: Type[SQLModel],
    db: Session, 
):
    entity = db.exec(select(EntityClass).where(EntityClass.id == entity_uuid)).one_or_none()

    if not entity:
        raise HTTPException(status_code=404, detail=f"{EntityClass.__translated_name__} no encontrado")

    setattr(entity, "is_active", True)
    db.commit()

    redirect_url = request.url_for(f"get_{EntityClass.__tablename__}", entity_uuid=entity_uuid)
    return RedirectResponse(url=redirect_url, status_code=303)

from fastapi import HTTPException


async def get_all_entities(
    *,
    request: Request,
    templates: Jinja2Templates,
    db: Session,
    EntityClass: Type[SQLModel],
    template_name: str,
    enum_fields: list = None,
    extra_db_fields: list = None,
    hero_title: str = None,
    hero_subtitle: str = None
):
    # Build the query to fetch data from the database
    statement = select(EntityClass).options(*extra_db_fields) if extra_db_fields else select(EntityClass)
    entities = db.exec(statement).all()

    if not entities:
        raise HTTPException(status_code=404, detail=f"No se encontraron {EntityClass.__translated_name__}s")

    fields=list(entities[0].__dict__.keys())
                
    for entity in entities:
        # Iterate over all fields of the entity (attributes)
        for field in fields:
            value = getattr(entity, field, None)
            
            # If the value is None or an empty string, remove the field entirely
            if value is None or value == '':
                delattr(entity, field)
            elif hasattr(value, 'value'):
                # If it's an enum, set the value to its enum value
                setattr(entity, field, value.value)
    
    # Set default values for hero_title and hero_subtitle if they were not passed
    if not hero_title:
        hero_title = f"{EntityClass.__translated_name__}s".capitalize()
    if not hero_subtitle:
        hero_subtitle = f"Explora todos los {EntityClass.__translated_name__}s registrados"

    # Render the HTML template with the data
    return templates.TemplateResponse(template_name, {
        "request": request,
        "entities_data": entities,
        "hero_title": hero_title,
        "hero_subtitle": hero_subtitle
    })