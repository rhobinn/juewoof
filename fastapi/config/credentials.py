import os
from dotenv import load_dotenv
from pathlib import Path

dotenv_path = Path(__file__).resolve().parents[2] / '.env'
print(dotenv_path)
load_dotenv(dotenv_path=dotenv_path)

JUEWOOF_DB_DRVR=os.environ.get('JUEWOOF_DB_DRVR')
JUEWOOF_DB_HOST=os.environ.get('JUEWOOF_DB_HOST')
JUEWOOF_DB_USER=os.environ.get('POSTGRES_USER')
JUEWOOF_DB_PASS=os.environ.get('POSTGRES_PASSWORD')
JUEWOOF_DB_NAME=os.environ.get('POSTGRES_DB')
JUEWOOF_DB_PORT=os.environ.get('EXPOSED_POSTGRES_PORT')

from sqlalchemy.engine import URL
DB_URL = URL.create(
    drivername=JUEWOOF_DB_DRVR,
    username=JUEWOOF_DB_USER,
    password=JUEWOOF_DB_PASS,
    host=JUEWOOF_DB_HOST,
    port=JUEWOOF_DB_PORT,
    database=JUEWOOF_DB_NAME,
)


STRIPE_SECRET_KEY=os.environ.get('STRIPE_SECRET_KEY')
