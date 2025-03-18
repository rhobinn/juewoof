from fastapi import FastAPI

app = FastAPI()


### Database

from sqlmodel import SQLModel, create_engine
from config.credentials import DB_URL
from sqlmodel import Session

db_engine = create_engine(DB_URL, echo=True)
def create_db_and_tables(db_engine=db_engine):
    SQLModel.metadata.create_all(db_engine)
    
@app.on_event("startup")
def on_startup():
    create_db_and_tables()

def get_session() -> Session:
    with Session(db_engine) as session:
        yield session


### Routers & Static Folders

from fastapi.staticfiles import StaticFiles
from routers.global_.routes import global_router
app.include_router(global_router)
app.mount("/static", StaticFiles(directory="static"), name="static")

from routers.dogs.routes import dogs_router
app.include_router(dogs_router, prefix="/dogs", tags=["dogs"])
app.mount("/routers/dogs/static", StaticFiles(directory="routers/dogs/static"), name="static_dogs")

from routers.products.routes import products_router
app.include_router(products_router, prefix="/products", tags=["products"])
app.mount("/routers/products/static", StaticFiles(directory="routers/products/static"), name="static_products")


from routers.stripe.routes import stripe_router
app.include_router(stripe_router, prefix="/stripe", tags=["stripe"])



# from apscheduler.schedulers.asyncio import AsyncIOScheduler
# from apscheduler.triggers.interval import IntervalTrigger
# from utils.idempotency import clean_old_idempotency_keys

# # Create an instance of the scheduler
# scheduler = AsyncIOScheduler()

# # Schedule the cron job (this will run once every 24 hours)
# scheduler.add_job(
#     clean_old_idempotency_keys,
#     IntervalTrigger(days=1),  # Adjust the interval as needed
#     id="clean_idempotency_keys",  # Job ID
#     name="Clean idempotency keys every 24 hours",  # Job name
#     replace_existing=True,
# )

# # Start the scheduler when the app starts
# @app.on_event("startup")
# async def startup():
#     print("Starting scheduler")
#     scheduler.start()

# # Example endpoint to create an idempotency key
# @app.post("/idempotency-key/")
# async def create_idempotency_key(key: str):
#     # Functionality to create idempotency key
#     return {"message": "Idempotency key created", "key": key}