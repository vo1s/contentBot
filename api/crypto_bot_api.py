from aiocryptopay import AioCryptoPay, Networks

from config import config

crypto_bot = AioCryptoPay(token=config.crypto_bot_token.get_secret_value(), network=Networks.TEST_NET)
