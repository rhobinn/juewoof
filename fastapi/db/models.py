from db.enums import MexicoStates, Genero, Tamano, Temperamento, PricingType
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import date, datetime, timezone
from pydantic import field_validator
from typing import List, Optional
import uuid

class ActiveMixin():
    is_active: bool = Field(default=True)

class UUIDMixin():
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

class CreatedByMixin(SQLModel):
    created_by: Optional[uuid.UUID] = Field(default=None, foreign_key="user.id")

class TimestampsMixin():
    time_created: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
    time_updated: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc), 
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)}
    )
class IdempotencyKey(SQLModel, TimestampsMixin, UUIDMixin, table=True):
    key: str = Field(unique=True, index=True)
    created_object_id: Optional[uuid.UUID] = Field(default=None, index=True)
    created_object_type: Optional[str] = Field(default=None, index=True)

class UserBase(SQLModel):
    nombre: str = Field(max_length=100)
    apellido_paterno: Optional[str] = None
    apellido_materno: Optional[str] = None
    email: str = Field(unique=True) 
    celular: Optional[str] = None
    calle: Optional[str] = None
    numero_exterior: Optional[str] = None
    numero_interior: Optional[str] = None
    municipio: Optional[str] = None
    estado: Optional[MexicoStates] = None
    codigo_postal: Optional[str] = None
    # @field_validator("nombre","apellido_paterno","")
    # @classmethod
    # def capitalize_name(cls, v: str) -> str:
    #     return v.capitalize()

class User(UserBase, TimestampsMixin, ActiveMixin, UUIDMixin, table=True):
    __tablename__ = "user"
    __translated_name__ = "usuario"
    dogs: List["Dog"] = Relationship(back_populates="tutor")
    compras: List["Purchase"] = Relationship(back_populates="user")

class UserCreate(UserBase):
    pass

class DogBase(SQLModel):
    nombre: str = Field(...,)
    raza: Optional[str] = Field(None,)
    peso: float = Field(...,)
    genero: Genero = Field(...,)
    tamano: Tamano = Field(...,)
    temperamento: Temperamento = Field(...,)
    fecha_nacimiento: date = Field(...,)
    is_vaccinated: bool = Field(default=False,)
    is_neutered: bool = Field(default=False,)
    color: Optional[str] = Field(None,)
    microchip_id: Optional[str] = Field(None,)
    alergias: Optional[str] = Field(None,)
    ultima_desparasitacion: Optional[date] = Field(None,)

    @field_validator('fecha_nacimiento', 'ultima_desparasitacion')
    @classmethod
    def check_date_is_past(cls, v: date) -> date:
        if not v:
            return None
        if v >= date.today():
            raise ValueError('La fecha debe ser anterior a hoy.')
        return v
    # @field_validator("nombre")
    # @classmethod
    # def capitalize_name(cls, v: str) -> str:
    #     return v.capitalize()

class Dog(DogBase, TimestampsMixin, ActiveMixin, UUIDMixin, table=True):
    __tablename__ = "dog"
    __translated_name__ = "perro"

    tutor_id: uuid.UUID = Field(foreign_key="user.id")  
    photo_path: Optional[str] = Field(None,)
    tutor: User = Relationship(back_populates="dogs")

class DogCreate(DogBase):
    pass

class ProductBase(SQLModel):
    nombre: str = Field(max_length=255)
    descripcion: Optional[str] = None
    # @field_validator("nombre")
    # @classmethod
    #def capitalize_name(cls, v: str) -> str:
    #     return v.capitalize()

class Product(ProductBase, TimestampsMixin, ActiveMixin, UUIDMixin, table=True):
    __tablename__ = "product"
    __translated_name__ = "producto"
    photo_path: Optional[str] = Field(None,)
    precios: Optional[List["Price"]] = Relationship(
        back_populates="producto",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )

class ProductCreate(ProductBase):
    pass

class PriceBase(SQLModel):
    producto_id: uuid.UUID = Field(foreign_key="product.id")
    cantidad: int  # Stored in cents (e.g., $10.00 → 1000)
    currency: str = Field(default="usd")
    precio_tipo: PricingType = Field(default=PricingType.FLAT)  # Each precio has its own type
    # frequency: SubscriptionFrequency = Field(default=SubscriptionFrequency.MONTHLY)  # Each precio has its own type

class Price(PriceBase, TimestampsMixin, ActiveMixin, UUIDMixin, table=True):
    __tablename__ = "price"
    __translated_name__ = "precio"
    producto: Optional[Product] = Relationship(back_populates="precios")

class PriceCreate(PriceBase):
    pass

class PurchaseBase(SQLModel):
    user_id: uuid.UUID = Field(foreign_key="user.id")
    producto_id: uuid.UUID = Field(foreign_key="product.id")
    precio_id: uuid.UUID = Field(foreign_key="price.id")

class Purchase(PurchaseBase, TimestampsMixin, ActiveMixin, UUIDMixin, table=True):
    user: Optional[User] = Relationship(back_populates="compras")
    producto: Optional[Product] = Relationship()
    precio: Optional[Price] = Relationship()

class PurchaseCreate(PurchaseBase):
    pass