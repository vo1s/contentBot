import httpx
import asyncio

BASE_URL = "https://lk.cactuspay.pro/api/"


async def create_payment(token: str, amount: int, order_id: str = None, description: str = None, h2h: bool = False,
                         user_ip: str = None):
    url = BASE_URL + "?method=create"
    payload = {
        "token": token,
        "amount": amount
    }
    if order_id:
        payload["order_id"] = order_id
    if description:
        payload["description"] = description
    if h2h:
        payload["h2h"] = h2h
        if not user_ip:
            raise ValueError("user_ip is required when h2h is True")
        payload["user_ip"] = user_ip

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            data = response.json()
            return data['response']['url']
        else:
            return response.text


async def get_payment_info(token: str, order_id: str):
    url = BASE_URL + "?method=get"
    payload = {
        "token": token,
        "order_id": order_id
    }

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            return {"status": "error", "response": response.text}