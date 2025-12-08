import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

load_dotenv()

DATABASE_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)


def get_room_info(room_number):
    """Получает информацию о кабинете из БД (case-insensitive)"""
    session = Session()
    try:
        query = text("""
            SELECT number, description, floor, photo_urls 
            FROM rooms 
            WHERE UPPER(number) = UPPER(:room_number)
        """)
        result = session.execute(query, {"room_number": room_number})
        room = result.fetchone()

        if room:
            return {
                "number": room[0],
                "description": room[1],
                "floor": room[2],
                "photo_urls": room[3] if room[3] else []
            }
        return None
    finally:
        session.close()


# Тестовая функция
if __name__ == "__main__":
    room = get_room_info("112")
    if room:
        print(f"✅ Найден кабинет {room['number']}")
        print(f"   Фото: {len(room['photo_urls'])} шт")
        for url in room['photo_urls']:
            print(f"   - {url}")
    else:
        print("❌ Кабинет 112 не найден")