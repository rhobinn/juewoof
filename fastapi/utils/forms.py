def snake_to_camel(snake_str: str) -> str:
    components = snake_str.split('_')
    return ''.join(x.capitalize() for x in components)


def generate_options_dict(fields_with_options):
    """
    Generates a dictionary of options for each field in the provided list of fields.
    Each field is expected to be associated with an Enum class in database.models.
    
    The dictionary's keys and values are the Enum member values.
    """
    import database.enums
    from enum import Enum
    select_options_dict = {}

    for field in fields_with_options:
        # Capitalize the field name to match the Enum class naming convention
        enum_class = getattr(database.enums, snake_to_camel(field), None)

        # If the Enum class exists, create a dictionary from the Enum members
        # Is enum_class a class object?
        # Is enum_class a subclass of Enum?

        if enum_class and isinstance(enum_class, type) and issubclass(enum_class, Enum):
            select_options_dict[field] = {member.value: member.value for member in enum_class}

    return select_options_dict

from fastapi import Request
from fastapi.responses import RedirectResponse
from database.models import IdempotencyKey
from sqlmodel import Session, select

def handle_idempotency_key(
        db: Session, 
        idempotency_key: str, 
        request: Request
    ) -> RedirectResponse:

    # First, check if the idempotency_key exists in the IdempotencyKey table
    stmt = select(IdempotencyKey).filter(IdempotencyKey.key == idempotency_key)
    existing_idempotency_key = db.exec(stmt).first()  # Use exec() to execute the query and fetch the first result
    
    if existing_idempotency_key:
        # If it exists, redirect to the existing entity based on the stored object type and id
        entity_class_name = existing_idempotency_key.created_object_type.lower()  # Assumes stored type matches the entity name
        redirect_url = request.url_for(f"get_{entity_class_name}", entity_uuid=existing_idempotency_key.created_object_id)
        return RedirectResponse(url=redirect_url, status_code=303)

    return None  # If no existing idempotency key is found, allow the creation of a new entity in the route
