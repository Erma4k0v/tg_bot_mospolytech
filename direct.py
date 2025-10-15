import os
from dotenv import load_dotenv

from pathlib import Path
load_dotenv(Path('.') / '.env')

print("DB_USER:", os.getenv('DB_USER'))
print("DB_HOST:", os.getenv('DB_HOST'))

DATABASE_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
print("DATABASE_URL:", DATABASE_URL.replace(os.getenv('DB_PASSWORD'), '***'))

from sqlalchemy import create_engine, text

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as connection:
        result = connection.execute(text("SELECT version();"))
        print("Успех! Версия БД:", result.fetchone()[0])
except Exception as e:
    print("Ошибка подключения:", e)