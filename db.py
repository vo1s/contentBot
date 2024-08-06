from config import config
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Literal
from datetime import datetime

db = AsyncIOMotorClient(config.db.get_secret_value())[config.db_name.get_secret_value()]


# Функция для получения коллекции пользователей
def get_users_collection():
    return db.users


# Функция для получения коллекции контента
def get_content_collection():
    return db.content


def get_videos_collection():
    return db.videos


# Пример асинхронной функции для добавления пользователя
async def add_user(user_data):
    users_collection = get_users_collection()
    if await users_collection.find_one({"_id": user_data["_id"]}) is None:
        await users_collection.insert_one(user_data)
    else:
        # Пользователь уже существует, можно обновить данные или игнорировать
        pass


async def add_user_data(user_id, username):
    user_data = {
        "_id": user_id,
        "username": username if username else None,
        "subscription_status": "free",
        "registration_date": datetime.now(),
        "balance": 10,
        "photo_index": 1,
        "max_photo_index": 1,
        "video_index": 1,
        "max_video_index": 1,
        "reff_info": {
            "reff_id": None,
            "refs": 0,
            "refs_bonus": 0,
            "level_1_bonus": 10,
            "level_2_bonus": 2.5,
            "earned_by_deposit": 0
        }

    }
    await add_user(user_data)


# Пример асинхронной функции для получения пользователя по ID
async def get_user_by_id(user_id: int):
    users_collection = get_users_collection()
    return await users_collection.find_one({"_id": user_id})


async def update_subscription_status(user_id, status):
    users_collection = get_users_collection()
    await users_collection.update_one({"_id": user_id}, {"$set": {"subscription_status": status}})


async def distribute_money_reffs(user_id: int, balance: int):
    users_collection = get_users_collection()
    user = await get_user_by_id(user_id)
    level_1_inviter = await get_user_by_id(user['reff_info']['reff_id'])
    if level_1_inviter is not None:  # НАЧИСЛЯЕМ БОНУС РЕФФЕРАЛУ ПЕРВОГО УРОВНЯ
        bonus = int(balance * int(level_1_inviter['reff_info']['level_1_bonus']) / 50) # сумма_поплнения * %первого уровня * 2
        await manage_balance(level_1_inviter['_id'], bonus, 'add')
        level_2_inviter = await get_user_by_id(level_1_inviter['reff_info']['reff_id'])
        if level_2_inviter is not None:  # НАЧИСЛЯЕМ БОНУС РЕФФЕРАЛУ ВТОРОГО УРОВНЯ
            bonus = int(balance * int(level_2_inviter['reff_info']['level_2_bonus']) / 50) # сумма_поплнения * %второго уровня * 2
            await manage_balance(level_2_inviter['_id'], bonus, 'add')


async def manage_balance(user_id: int, balance: int, operation: Literal["add", "subtract"]):
    users_collection = get_users_collection()
    user = await get_user_by_id(user_id)
    if not user:
        raise ValueError("User not found")

    if not await check_subscription(user_id):
        # проверка на отрицательный баланс
        if user['balance'] - balance < 0 and operation == "subtract":
            new_balance = 0
        else:
            new_balance = user['balance'] - balance if operation == "subtract" else user['balance'] + balance

        await users_collection.update_one(
            {"_id": user_id},
            {"$set": {"balance": new_balance}}
        )

        return new_balance


async def check_subscription(user_id: int) -> bool:
    user = await get_user_by_id(user_id)
    if user['subscription_status'] == "paid":
        return True
    return False


async def check_balance(user_id: int) -> bool:
    user = await get_user_by_id(user_id)
    if user['balance'] >= 2 or user['subscription_status'] == "paid":
        return True
    return False


async def update_page_index(user_id: int, page: int, collection, max_photo_index: int,
                            index: Literal["photo_index", "video_index"]):
    await collection.update_one(
        {"_id": user_id},
        {"$set": {index: page}},
    )
    if page >= max_photo_index:
        await collection.update_one(
            {"_id": user_id},
            {"$set": {f"max_{index}": page}},
        )


async def get_current_page_index(user_id: int, index: Literal["photo_index", "video_index"]) -> int:
    user = await get_user_by_id(user_id)
    return user[index]


async def get_photo(page: int):
    photo = await get_content_collection().find().skip(page - 1).limit(1).to_list(length=1)
    if photo:
        return photo[0]
    return None


async def get_video(page: int):
    video = await get_videos_collection().find().skip(page - 1).limit(1).to_list(length=1)
    if video:
        return video[0]
    return None
