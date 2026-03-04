import asyncio
import sqlite3
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

TOKEN = "8133134761:AAFi7aTDD3vCM78LhVKUqaK05kT7Avcsnmo"


conn = sqlite3.connect("users.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER,
    name TEXT,
    birthday TEXT,
    phone TEXT
)
""")
conn.commit()


class Register(StatesGroup):
    name = State()
    birthday = State()
    phone = State()

dp = Dispatcher()


@dp.message(Command("start"))
async def start_handler(message: Message, state: FSMContext):
    telegram_id = message.from_user.id

    cursor.execute("SELECT * FROM users WHERE telegram_id=?", (telegram_id,))
    user = cursor.fetchone()

    if user:
        await message.answer("Siz allaqachon ro'yxatdan o'tgansiz ")
        return

    await message.answer("Ro'yxatdan o'tish boshlandi.\nIsmingizni kiriting:")
    await state.set_state(Register.name)


@dp.message(Register.name)
async def get_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Tug'ilgan kuningizni kiriting :")
    await state.set_state(Register.birthday)


@dp.message(Register.birthday)
async def get_birthday(message: Message, state: FSMContext):
    await state.update_data(birthday=message.text)

    contact_btn = KeyboardButton(
        text="Telefon raqam yuborish",
        request_contact=True
    )

    keyboard = ReplyKeyboardMarkup(
        keyboard=[[contact_btn]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    await message.answer("Telefon raqamingizni yuboring:", reply_markup=keyboard)
    await state.set_state(Register.phone)


@dp.message(Register.phone, F.contact)
async def get_phone(message: Message, state: FSMContext):
    data = await state.get_data()

    cursor.execute("""
        INSERT INTO users (telegram_id, name, birthday, phone)
        VALUES (?, ?, ?, ?)
    """, (
        message.from_user.id,
        data["name"],
        data["birthday"],
        message.contact.phone_number
    ))
    conn.commit()

    await message.answer("Muvaffaqiyatli ro'yxatdan o'tdingiz ")
    await state.clear()


@dp.message(Register.phone)
async def wrong_phone(message: Message):
    await message.answer("Iltimos telefonni tugma orqali yuboring ")


@dp.message(Command("search"))
async def search_handler(message: Message):
    args = message.text.split()

    if len(args) < 2:
        await message.answer("Qidirish uchun:")
        return

    query = args[1]

    cursor.execute("""
        SELECT name, birthday, phone FROM users
        WHERE name LIKE ? OR phone LIKE ?
    """, (f"%{query}%", f"%{query}%"))

    results = cursor.fetchall()

    if not results:
        await message.answer("Hech narsa topilmadi ")
        return

    text = "Topilgan foydalanuvchilar:\n\n"
    for r in results:
        text += f"Ism: {r[0]}\nTug'ilgan sana: {r[1]}\nTelefon: {r[2]}\n\n"

    await message.answer(text)


async def main():
    bot = Bot(token=TOKEN)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
