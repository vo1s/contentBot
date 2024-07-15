import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from config import config

client = AsyncIOMotorClient("mongodb://localhost:27017/")
db = client[config.db_name.get_secret_value()]
videos_collection = db.videos

async def add_videos_to_db(directory):
    video_id = 1  # Начальный идентификатор для видео

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv')):
                file_path = os.path.join(root, file)
                video_data = {
                    "file_path": file_path,
                }
                await videos_collection.insert_one(video_data)
                video_id += 1
                print(f"Added {file_path}")

if __name__ == "__main__":
    directory = "/Users/vo1s/videos"  # Обновите путь к директории с видеофайлами
    loop = asyncio.get_event_loop()
    loop.run_until_complete(add_videos_to_db(directory))
