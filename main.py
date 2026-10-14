"""Простой Telegram-бот купонов для Bothost (polling + кнопки)."""

from __future__ import annotations

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Optional

from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = (
    os.getenv("BOT_TOKEN")
    or os.getenv("TELEGRAM_BOT_TOKEN")
    or os.getenv("API_TOKEN")
    or ""
).strip()

MANAGER_ID = int(os.environ["MANAGER_ID"])
COUPON_USER_ID = int(os.environ["COUPON_USER_ID"])

DATA_DIR = Path(os.getenv("DATA_DIR", "data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)
STORAGE_PATH = DATA_DIR / "coupons.json"

BTN_ADD = "➕ Выдать купон"
BTN_BALANCE = "🎫 Баланс"
BTN_USE = "✅ Списать купон"

router = Router()


def _load_count() -> int:
    if not STORAGE_PATH.exists():
        return 0
    try:
        data = json.loads(STORAGE_PATH.read_text(encoding="utf-8"))
        return max(0, int(data.get("coupons", 0)))
    except (json.JSONDecodeError, TypeError, ValueError):
        logger.warning("Broken storage file, resetting to 0")
        return 0


def _save_count(count: int) -> None:
    STORAGE_PATH.write_text(
        json.dumps({"coupons": count}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def manager_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=BTN_ADD)]],
        resize_keyboard=True,
    )


def user_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=BTN_BALANCE), KeyboardButton(text=BTN_USE)]],
        resize_keyboard=True,
    )


def keyboard_for(user_id: int) -> Optional[ReplyKeyboardMarkup]:
    if user_id == MANAGER_ID:
        return manager_keyboard()
    if user_id == COUPON_USER_ID:
        return user_keyboard()
    return None


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    user_id = message.from_user.id if message.from_user else 0
    kb = keyboard_for(user_id)

    if user_id == MANAGER_ID:
        await message.answer(
            "Вы менеджер.\nНажмите кнопку, чтобы выдать купон пользователю.",
            reply_markup=kb,
        )
        return

    if user_id == COUPON_USER_ID:
        count = _load_count()
        await message.answer(
            f"Привет! У вас купонов: {count}.\n"
            "Используйте кнопки ниже.",
            reply_markup=kb,
        )
        return

    await message.answer("Нет доступа к этому боту.")


@router.message(Command("add"))
@router.message(F.text == BTN_ADD)
async def add_coupon(message: Message, bot: Bot) -> None:
    user_id = message.from_user.id if message.from_user else 0
    if user_id != MANAGER_ID:
        await message.answer("Только менеджер может выдавать купоны.")
        return

    count = _load_count() + 1
    _save_count(count)

    await message.answer(
        f"Купон выдан. Баланс пользователя: {count}",
        reply_markup=manager_keyboard(),
    )

    try:
        await bot.send_message(
            COUPON_USER_ID,
            f"Вам выдан новый купон!\nТекущий баланс: {count}",
            reply_markup=user_keyboard(),
        )
    except Exception:
        logger.exception("Failed to notify coupon user")
        await message.answer(
            "Купон сохранён, но уведомить пользователя не удалось. "
            "Пусть он откроет бота и нажмёт Start."
        )


@router.message(Command("balance"))
@router.message(F.text == BTN_BALANCE)
async def balance(message: Message) -> None:
    user_id = message.from_user.id if message.from_user else 0
    if user_id not in (MANAGER_ID, COUPON_USER_ID):
        await message.answer("Нет доступа.")
        return

    count = _load_count()
    await message.answer(
        f"Баланс купонов: {count}",
        reply_markup=keyboard_for(user_id),
    )


@router.message(Command("use"))
@router.message(F.text == BTN_USE)
async def use_coupon(message: Message) -> None:
    user_id = message.from_user.id if message.from_user else 0
    if user_id != COUPON_USER_ID:
        await message.answer("Списывать купоны может только пользователь.")
        return

    count = _load_count()
    if count <= 0:
        await message.answer(
            "Нет доступных купонов.",
            reply_markup=user_keyboard(),
        )
        return

    count -= 1
    _save_count(count)
    await message.answer(
        f"Списан 1 купон. Осталось: {count}",
        reply_markup=user_keyboard(),
    )


async def main() -> None:
    if not BOT_TOKEN:
        raise SystemExit(
            "BOT_TOKEN не задан. Локально скопируйте .env.example → .env, "
            "на Bothost укажите токен в панели создания бота."
        )

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)

    logger.info(
        "Starting bot (manager=%s, user=%s, storage=%s)",
        MANAGER_ID,
        COUPON_USER_ID,
        STORAGE_PATH,
    )
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
