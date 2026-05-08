
import asyncio
import json
import os
import time

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton
)

TOKEN = "8652560896:AAFAY9FQyytlOpcg8pXR-MqGUs9zpL0SOEg"

bot = Bot(TOKEN)
dp = Dispatcher()

DB = "database.json"

if not os.path.exists(DB):
    with open(DB, "w", encoding="utf-8") as f:
        json.dump({}, f)


def load_db():
    with open(DB, "r", encoding="utf-8") as f:
        return json.load(f)


def save_db(data):
    with open(DB, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def get_user(user_id):
    data = load_db()

    if str(user_id) not in data:
        data[str(user_id)] = {
            "tokens": 100,
            "lost": 0,
            "prefix": "",
            "avatar": "",
            "inventory": [],
            "farms": [],
            "last_farm": 0
        }
        save_db(data)

    return data[str(user_id)]


def update_user(user_id, user_data):
    data = load_db()
    data[str(user_id)] = user_data
    save_db(data)


TOKENS_WORDS = [
    "/tokens",
    "токены",
    "баланс",
    "мешок"
]

FARM_WORDS = [
    "/farmer",
    "фарм",
    "ферма",
    "фармилка"
]

SHOP_WORDS = [
    "/chatshop",
    "шоп",
    "магазин",
    "стор"
]

BAG_WORDS = [
    "/yourbag",
    "инвентарь",
    "что у меня есть"
]


main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Баланс"),
            KeyboardButton(text="Фарм")
        ],
        [
            KeyboardButton(text="Шоп"),
            KeyboardButton(text="Инвентарь")
        ]
    ],
    resize_keyboard=True
)


shop_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="⭐ Привилегии")],
        [KeyboardButton(text="♦️ Баффы")],
        [KeyboardButton(text="🔸 ФермШоп")],
        [KeyboardButton(text="⬅️ Назад")]
    ],
    resize_keyboard=True
)


buffs_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="😄 Удаление сообщения")],
        [KeyboardButton(text="📌 Закрепить сообщение")],
        [KeyboardButton(text="🤐 Мут участников")],
        [KeyboardButton(text="🎭 Фейк префикс")],
        [KeyboardButton(text="🖼️ Ава Профиля")],
        [KeyboardButton(text="⬅️ Назад")]
    ],
    resize_keyboard=True
)


inventory_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Префиксы🎭")],
        [KeyboardButton(text="⬅️ Назад")]
    ],
    resize_keyboard=True
)


@dp.message(Command("start"))
async def start(message: Message):
    get_user(message.from_user.id)

    await message.answer(
        "⭐ Бот успешно запущен!",
        reply_markup=main_kb
    )


@dp.message()
async def all_messages(message: Message):
    if not message.text:
        return

    text = message.text.lower()

    user = get_user(message.from_user.id)

    # =========================
    # TOKENS
    # =========================

    if text in TOKENS_WORDS:

        await message.answer(
            f"⭐ Твой Баланс: {user['tokens']}\n\n"
            f"😓 Слито: {user['lost']}"
        )
        return

    # =========================
    # FARM
    # =========================

    if text in FARM_WORDS:

        if len(user["farms"]) == 0:
            await message.answer(
                "😓 У тебя нет ферм.\n"
                "Купи ферму в ФермШопе."
            )
            return

        now = time.time()
        cooldown = 86400
        remaining = int(cooldown - (now - user["last_farm"]))

        if remaining > 0:

            days = remaining // 86400
            hours = (remaining % 86400) // 3600
            minutes = (remaining % 3600) // 60

            await message.answer(
                f"⚙️ Осталось до сборки:\n"
                f"{days}д {hours}ч {minutes}м"
            )
            return

        total = 0
        result = ""

        for farm in user["farms"]:
            total += farm["income"]

            result += (
                f"🔶 Собрано из фермы "
                f"{farm['name']} : "
                f"{farm['income']}\n"
            )

        user["tokens"] += total
        user["last_farm"] = now

        update_user(message.from_user.id, user)

        result += "\n⚙️ Следующая сборка через 1 день"

        await message.answer(result)
        return

    # =========================
    # SHOP
    # =========================

    if text in SHOP_WORDS:

        await message.answer(
            f"📋 Приветствую "
            f"@{message.from_user.username}!\n\n"
            f"Выберите магазин.",
            reply_markup=shop_kb
        )
        return

    # =========================
    # FARM SHOP
    # =========================

    if text == "🔸 фермшоп":

        farms_count = len(user["farms"])

        if farms_count >= 3:
            await message.answer(
                "😓 Ошибка!\n\n"
                "Лимит ферм достигнут."
            )
            return

        if user["tokens"] < 25:
            await message.answer(
                "😓 Недостаточно токенов."
            )
            return

        user["tokens"] -= 25

        farm = {
            "name": f"Ферма #{farms_count + 1}",
            "income": 15,
            "level": 1,
            "price": 25
        }

        user["farms"].append(farm)

        update_user(message.from_user.id, user)

        await message.answer(
            "😉 Ферма была успешно куплена.\n"
            "Токены списаны."
        )
        return

    # =========================
    # INVENTORY
    # =========================

    if text in BAG_WORDS:

        await message.answer(
            f"🎒 Твой весь Инвентарь:\n\n"
            f"💰 Сколько предметов сейчас: "
            f"{len(user['inventory'])}\n"
            f"⏳ Сколько всего предметов: "
            f"{len(user['inventory'])}",
            reply_markup=inventory_kb
        )
        return

    # =========================
    # PREFIXES
    # =========================

    if text == "префиксы🎭":

        await message.answer(
            "🎭 Все префиксы которые у тебя есть\n\n"
            "★★★★★\n"
            "🟡 Легендарные: 0\n\n"
            "★★★★\n"
            "🔴 Мифические: 0\n\n"
            "★★★\n"
            "🟣 Эпические: 0\n\n"
            "★★\n"
            "🔵 Редкие: 0\n\n"
            "★\n"
            "🟢 Обычные: 0"
        )
        return

    # =========================
    # PRIVILEGES
    # =========================

    if text == "⭐ привилегии":

        await message.answer(
            "📋 Все привилегии в чате!\n\n"
            "⭐ VIP — 50 токенов\n"
            "⭐ PREMIUM — 100 токенов\n"
            "⭐ DELUXE — 250 токенов"
        )
        return

    # =========================
    # BUFFS
    # =========================

    if text == "♦️ баффы":

        await message.answer(
            "♦️ Мелкие баффы которые можно купить",
            reply_markup=buffs_kb
        )
        return

    # =========================
    # DELETE MESSAGE BUFF
    # =========================

    if text == "😄 удаление сообщения":

        if user["tokens"] < 10:
            await message.answer(
                "😓 Недостаточно токенов."
            )
            return

        user["tokens"] -= 10
        update_user(message.from_user.id, user)

        await message.answer(
            "😉 Бафф успешно куплен.\n\n"
            "📋 Ответьте на сообщение "
            "которое хотите удалить."
        )
        return

    # =========================
    # PIN MESSAGE BUFF
    # =========================

    if text == "📌 закрепить сообщение":

        if user["tokens"] < 15:
            await message.answer(
                "😓 Недостаточно токенов."
            )
            return

        user["tokens"] -= 15
        update_user(message.from_user.id, user)

        await message.answer(
            "😉 Бафф успешно куплен.\n\n"
            "📋 Ответьте на сообщение "
            "которое хотите закрепить."
        )
        return

    # =========================
    # MUTE BUFF
    # =========================

    if text == "🤐 мут участников":

        if user["tokens"] < 20:
            await message.answer(
                "😓 Недостаточно токенов."
            )
            return

        user["tokens"] -= 20
        update_user(message.from_user.id, user)

        await message.answer(
            "😉 Бафф успешно куплен.\n\n"
            "📋 Ответьте на сообщение "
            "пользователя которого хотите замутить."
        )
        return

    # =========================
    # FAKE PREFIX
    # =========================

    if text == "🎭 фейк префикс":

        if user["tokens"] < 30:
            await message.answer(
                "😓 Недостаточно токенов."
            )
            return

        user["tokens"] -= 30

        user["prefix"] = "👑 OWNER"

        update_user(message.from_user.id, user)

        await message.answer(
            "🎭 Префикс был успешно установлен!\n\n"
            "👀 Чтобы посмотреть профиль "
            "напишите /profile"
        )
        return

    # =========================
    # AVATAR
    # =========================

    if text == "🖼️ ава профиля":

        if user["tokens"] < 35:
            await message.answer(
                "😓 Недостаточно токенов."
            )
            return

        user["tokens"] -= 35
        update_user(message.from_user.id, user)

        await message.answer(
            "🖼️ Фото профиля успешно поменяно!"
        )
        return

    # =========================
    # BACK BUTTON
    # =========================

    if text == "⬅️ назад":

        await message.answer(
            "🏠 Главное меню",
            reply_markup=main_kb
        )
        return


@dp.message(Command("profile"))
async def profile(message: Message):

    user = get_user(message.from_user.id)

    farms = len(user["farms"])

    await message.answer(
        f"👤 Профиль @{message.from_user.username}\n\n"
        f"⭐ Токены: {user['tokens']}\n"
        f"🎭 Префикс: {user['prefix']}\n"
        f"🔶 Ферм: {farms}"
    )


async def main():
    print("Bot started...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
