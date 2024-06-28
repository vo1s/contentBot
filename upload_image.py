import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from config import config

# Подключение к MongoDB
client = AsyncIOMotorClient("mongodb://localhost:27017/")
db = client[config.db_name.get_secret_value()]
photos_collection = db.content


async def add_photos_to_db(directory):
    photo_id = 1  # Начальный идентификатор для фотографий

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                file_path = os.path.join(root, file)
                photo_data = {
                    "file_path": file_path,
                }
                await photos_collection.insert_one(photo_data)
                photo_id += 1
                print(f"Added {file_path}")


if __name__ == "__main__":
    directory = "/Users/vo1s/photos"
    loop = asyncio.get_event_loop()
    loop.run_until_complete(add_photos_to_db(directory))
