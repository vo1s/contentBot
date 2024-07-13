from config import config
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Literal

db = AsyncIOMotorClient("mongodb://localhost:27017/")[config.db_name.get_secret_value()]


# Функция для получения коллекции пользователей
def get_users_collection():
    return db.users


# Функция для получения коллекции контента
def get_content_collection():
    return db.content


# Пример асинхронной функции для добавления пользователя
async def add_user(user_data):
    users_collection = get_users_collection()
    if await users_collection.find_one({"_id": user_data["_id"]}) is None:
        await users_collection.insert_one(user_data)
    else:
        # Пользователь уже существует, можно обновить данные или игнорировать
        pass


# Пример асинхронной функции для получения пользователя по ID
async def get_user_by_id(user_id: int):
    users_collection = get_users_collection()
    return await users_collection.find_one({"_id": user_id})


async def update_subscription_status(user_id, status):
    users_collection = get_users_collection()
    await users_collection.update_one({"_id": user_id}, {"$set": {"subscription_status": status}})


async def manage_balance(user_id: int, balance: int, operation: Literal["add", "subtract"]):
    users_collection = get_users_collection()
    user = await get_user_by_id(user_id)
    if not user:
        raise ValueError("User not found")

    # проверка на отрицательный баланс
    if user['balance'] - balance < 0:
        new_balance = 0
    else:
        new_balance = user['balance'] - balance if operation == "subtract" else user['balance'] + balance

    await users_collection.update_one(
        {"_id": user_id},
        {"$set": {"balance": new_balance}}
    )

    return new_balance


async def check_balance(user_id: int) -> bool:
    user = await get_user_by_id(user_id)
    if user['balance'] >= 2 or user['subscription_status'] == "paid":
        return True
    return False


async def update_page_index(user_id: int, page: int, collection, max_photo_index: int):
    await collection.update_one(
        {"_id": user_id},
        {"$set": {"photo_index": page}},
    )
    if page >= max_photo_index:
        await collection.update_one(
            {"_id": user_id},
            {"$set": {"max_photo_index": page}},
        )


async def get_current_page_index(user_id: int) -> int:
    user = await get_user_by_id(user_id)
    return user['photo_index']
