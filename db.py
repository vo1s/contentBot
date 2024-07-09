from typing import Literal

import pymongo
from pymongo import MongoClient
from config import config
from motor.motor_asyncio import AsyncIOMotorClient

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

    new_balance = user['balance'] - balance if operation == "subtract" else user['balance'] + balance

    await users_collection.update_one(
        {"_id": user_id},
        {"$set": {"balance": new_balance}}
    )

    return new_balance