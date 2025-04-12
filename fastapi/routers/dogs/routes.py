from fastapi import APIRouter, Request, Depends, Body
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlmodel import Session
from main import get_session
import uuid 
from utils.crud import create_entity, update_entity, get_create_view, get_read_view, get_update_view, deactivate_entity, activate_entity, get_all_entities
from core.auth import get_current_user

from database.models import DogCreate, Dog, User

dogs_router = APIRouter()

dogs_templates = Jinja2Templates(directory=["routers/global_/templates", "routers/dogs/templates"])

@dogs_router.get("/home", response_class=HTMLResponse)
async def home(request: Request, user: dict = Depends(get_current_user)):

    return dogs_templates.TemplateResponse("home.html", {"request": request, "user": user})

### CREATE | GET : WEBVIEW - Creation of a dog
@dogs_router.get("/create", response_class=HTMLResponse)
async def create_dog_form(request: Request,
                          user: dict = Depends(get_current_user)
                          ):

    fields_with_options = ['genero', 'tamano', 'temperamento']
    
    return get_create_view(
        request=request,
        templates=dogs_templates, 
        template_name="dogs_create.html",
        fields_with_options=fields_with_options,
        hero_title="Agregar perrito",
        hero_subtitle="",
        user=user,
    )

### CREATE | POST - Creation of a dog
@dogs_router.post("/create")
async def create_dog(   request: Request, 
                        entity_data: DogCreate = Body(...), 
                        db: Session = Depends(get_session),
                        user: dict = Depends(get_current_user)
                        ):  
    
    return create_entity(
        request=request, 
        entity_data=entity_data, 
        EntityClass=Dog, 
        db=db, 
        extra_fields={"tutor_id": user['id']}
    )

### READ | GET: WEBVIEW- View info of a single dog
@dogs_router.get("/{entity_uuid}")
async def get_dog(request: Request, 
                  entity_uuid: uuid.UUID, 
                  db: Session = Depends(get_session),
                  user: dict = Depends(get_current_user)
                  ):

    return get_read_view(
        request=request,
        templates=dogs_templates,
        entity_uuid=entity_uuid,
        EntityClass=Dog,
        db=db,
        template_name="dogs_read.html",
        hero_title="Información del perro",
        hero_subtitle="",
        extra_fields=['tutor'],
        user=user
    )

#     hero_title=entity.nombre.capitalize()
#     hero_subtitle=entity.tutor.apellido_paterno.capitalize()+" "+entity.tutor.apellido_materno.capitalize()


### UPDATE | POST - update info of a dog 
@dogs_router.patch("/update/{entity_uuid}")
async def update_dog(   request: Request, 
                        entity_uuid: uuid.UUID, 
                        entity_data: DogCreate = Body(...), 
                        db: Session = Depends(get_session),
                    ):  
    return update_entity(
        request=request, 
        entity_uuid=entity_uuid, 
        entity_data=entity_data, 
        db=db, 
        EntityClass=Dog
    )
### UPDATE | GET: WEBVIEW - update info of a dog 
@dogs_router.get("/update/{entity_uuid}")
async def update_dog_form(  request: Request,
                            entity_uuid: uuid.UUID, 
                            db: Session = Depends(get_session),
                            user: dict = Depends(get_current_user)
                        ):

    return get_update_view(
        request=request,
        templates=dogs_templates,
        entity_uuid=entity_uuid,
        EntityClass=Dog,
        fields_with_options=['genero','tamano','temperamento'],
        extra_fields=['tutor','is_active'],
        template_name="dogs_update.html",
        hero_title="Actualizar",
        hero_subtitle="Actualiza los detalles del Perro",
        user=user,
        db=db,
    )


### DEACTIVATE | PATCH - Deactivate a dog
@dogs_router.patch("/deactivate/{entity_uuid}")
async def deactivate_dog(request: Request, entity_uuid: uuid.UUID, db: Session = Depends(get_session)):
    return deactivate_entity(   request=request,
                                entity_uuid=entity_uuid,
                                EntityClass=Dog,
                                db=db, 
                            )
### ACTIVATE | PATCH - Deactivate a dog
@dogs_router.patch("/activate/{entity_uuid}")
async def activate_dog(request: Request, entity_uuid: uuid.UUID, db: Session = Depends(get_session)):
    return activate_entity(   request=request,
                                entity_uuid=entity_uuid,
                                EntityClass=Dog,
                                db=db, 
                            )

from sqlalchemy.orm import selectinload

### INDEX(ALL)| GET : WEBVIEW  View info of all dogs 
@dogs_router.get("/index/all", response_class=HTMLResponse)  
async def get_all_dogs(request: Request, 
                       db: Session = Depends(get_session),
                       user: dict = Depends(get_current_user),
                       ):
    return await get_all_entities(  request=request,
                                    templates=dogs_templates,
                                    db=db,
                                    EntityClass=Dog,
                                    template_name="dogs_index.html",
                                    enum_fields=['genero', 'tamano', 'temperamento'],
                                    extra_db_fields=[selectinload(Dog.tutor)], 
                                    hero_title=None,
                                    hero_subtitle=None,
                                    user=user
                                    )


### INDEX(MY)| GET : WEBVIEW  View info of all dogs from the signed-in-user's dogs
@dogs_router.get("/index/my", response_class=HTMLResponse)  
async def get_my_dogs(  request: Request, 
                        db: Session = Depends(get_session),
                        user: dict = Depends(get_current_user)
                    ):

    print("usuario: ", user)
    from main import app
    print("usuarioAPP: ", app.state.is_user_logged_in)

    statement = select(User).where(User.id == user['id'])
    tutor = db.exec(statement).one_or_none()

    if tutor is None:
        raise HTTPException(status_code=404, detail="Tutor not found")

    active_dogs = [dog for dog in tutor.dogs if dog.is_active]

    #Get the string values of the enums
    for dog in active_dogs:
        dog.genero = dog.genero.value
        dog.tamano = dog.tamano.value
        dog.temperamento = dog.temperamento.value

    hero_title="Mis perritos"
    hero_subtitle=tutor.dogs[0].tutor.nombre.capitalize()+" "+tutor.dogs[0].tutor.apellido_materno.capitalize()

    return dogs_templates.TemplateResponse("dogs_index.html", {"request": request,
                                                               "entities_data":active_dogs, 
                                                               "hero_title":hero_title, 
                                                               "hero_subtitle":hero_subtitle, 
                                                               "user":user
                                                               })

from sqlmodel import select
from typing import List
from fastapi import HTTPException

### INDEX(USER)| GET : WEBVIEW  View info of all dogs from an especific  tutor 
@dogs_router.get("/index/tutor/{tutor_uuid}", response_class=HTMLResponse)  
async def get_user_dogs(request: Request,
                        tutor_uuid: uuid.UUID,
                        db: Session = Depends(get_session),
                        user: dict = Depends(get_current_user)
                        ):
    statement = select(User).where(User.id == tutor_uuid)
    tutor = db.exec(statement).one_or_none()

    if tutor is None:
        raise HTTPException(status_code=404, detail="Tutor not found")

    #Get the string valus of the enums
    for dog in tutor.dogs:
        dog.genero = dog.genero.value
        dog.tamano = dog.tamano.value
        dog.temperamento = dog.temperamento.value

    hero_title="Los perritos de"
    hero_subtitle=tutor.dogs[0].tutor.nombre.capitalize()+" "+tutor.dogs[0].tutor.apellido_materno.capitalize()
    return dogs_templates.TemplateResponse("dogs_index.html", {"request": request,
                                                               "entities_data":tutor.dogs,
                                                               "hero_title":hero_title,
                                                               "hero_subtitle":hero_subtitle,
                                                               "user":user
                                                               })

