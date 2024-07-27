from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.utils.keyboard import InlineKeyboardBuilder


def deposit_keyboard():
    buttons = [
        [
            InlineKeyboardButton(text="💰Пополнить", callback_data=f"enter_money"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

#Клавиатура на подписку
def payment_keyboard_subscription(rub_amount: int):
    buttons = [
        [
            InlineKeyboardButton(text="🪙CryptoBot", callback_data=f"pay_crypto_keyboard:{rub_amount}"),
        ],
        [
            InlineKeyboardButton(text="💸Оплата через администратора(рубли)", callback_data=f"pay_by_hand:{rub_amount}"),
        ],
        [
            InlineKeyboardButton(text="💵Stars (самый удобный)", callback_data=f"pay_stars_subscription"),
        ],

    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def stars_keyboard_subscription():
    buttons = [
        [
            InlineKeyboardButton(text="137⭐- 299 RUB", callback_data=f"create_stars_invoice:137:299"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# Клавиатура на депозит
def payment_keyboard(rub_amount: int):
    buttons = [
        [
            InlineKeyboardButton(text="🪙CryptoBot", callback_data=f"pay_crypto_keyboard:{rub_amount}"),
        ],
        [
            InlineKeyboardButton(text="💸Оплата через администратора(рубли)", callback_data=f"pay_by_hand:{rub_amount}"),
        ],
        [
            InlineKeyboardButton(text="💵Stars (самый удобный)", callback_data=f"pay_stars:{rub_amount}"),
        ],

    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def stars_keyboard():
    buttons = [
        [
            InlineKeyboardButton(text="30⭐- 66 RUB", callback_data=f"create_stars_invoice:30:66"),
            InlineKeyboardButton(text="50⭐- 115 RUB", callback_data=f"create_stars_invoice:50:115"),
            InlineKeyboardButton(text="1⭐- 100 RUB", callback_data=f"create_stars_invoice:1:1"),
        ],
        [
            InlineKeyboardButton(text="100⭐- 230 RUB", callback_data=f"create_stars_invoice:100:230"),
            InlineKeyboardButton(text="200⭐- 450 RUB", callback_data=f"create_stars_invoice:200:450"),

        ],
        [
            InlineKeyboardButton(text="300⭐- 680 RUB", callback_data=f"create_stars_invoice:300:680"),
        ],

    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def payment_keyboard_stars(stars_amount: int):
    builder = InlineKeyboardBuilder()
    builder.button(text=f"Оплатить {stars_amount} ⭐️", pay=True)

    return builder.as_markup()


def currencies(rub_amount: int):
    buttons = [
        [
            InlineKeyboardButton(text="🪙USDT", callback_data=f"create_invoice_crypto:USDT:{rub_amount}"),
            InlineKeyboardButton(text="🔷TON", callback_data=f"create_invoice_crypto:TON:{rub_amount}"),
        ],
        [
            InlineKeyboardButton(text="🤑BTC", callback_data=f"create_invoice_crypto:BTC:{rub_amount}"),
            InlineKeyboardButton(text="🤑ETH", callback_data=f"create_invoice_crypto:ETH:{rub_amount}"),
        ],
        [
            InlineKeyboardButton(text="🔙Назад", callback_data=f"back_to_pay_menu"),
        ],

    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def check_crypto_bot_payment_keyboard(invoice_id: int, url: str, rub_amount: int):
    buttons = [
        [
            InlineKeyboardButton(text="Оплатить", url=url),
        ],
        [
            InlineKeyboardButton(text="🔍Проверить оплату",
                                 callback_data=f"check_crypto_bot_payment:{invoice_id}:{rub_amount}"),
        ],
        [
            InlineKeyboardButton(text="🔙Назад", callback_data=f"pay_crypto_keyboard:{rub_amount}"),
        ],

    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
