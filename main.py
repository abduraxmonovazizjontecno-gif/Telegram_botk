from csv import DictReader
from tkinter.font import names

from aiogram import F
import csv
from aiogram.filters import Command
import json
import asyncio
import logging
import sys
from datetime import datetime
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery
from datetime import datetime

from aiogram.utils.keyboard import InlineKeyboardBuilder

from models import District,Region
redis_url = 'redis://localhost:6379/0'
dp = Dispatcher(storage=RedisStorage.from_url(redis_url))

TOKEN = "8133134761:AAFi7aTDD3vCM78LhVKUqaK05kT7Avcsnmo"
ADMIN_ID = 6341903269

#
# class Form(StatesGroup):
#     first_name = State()
#     birthdate = State()
#     image = State()
#
#
# @dp.message(Form.first_name)
# async def command(message: Message, state: FSMContext) -> None:
#     await state.update_data(first_name=message.text)
#     await state.set_state(Form.birthdate)
#     await message.answer("Tug'ilgan kunizni kiriting : ")
#
#
# @dp.message(Form.birthdate)
# async def get_birthdate(message: Message, state: FSMContext) -> None:
#     try:
#         year = int(message.text)
#         current_year = datetime.now().year
#         age = current_year - year
#         if age > 18:
#             await state.update_data(birthdate=year, age=age)
#             await state.set_state(Form.image)
#             await message.answer("Rasmizni yuboring:")
#         else:
#             await message.reply("Yoshiz 18 dan katta bo'lishi kerak")
#
#     except ValueError:
#         await message.reply("Iltimos, to‘g‘ri yil kiriting (masalan: 2005)")
#
#
# @dp.message(Form.image)
# async def command(message: Message, state: FSMContext) -> None:
#     if message.photo is None:
#         await message.reply('Rasmizni  tashlang (rasm formatda kelsin)')
#         return
#
#     file_id = message.photo[-1].file_id
#     await state.update_data(image=file_id)
#     data = await state.get_data()
#     await state.clear()
#     text = (f"<b>Name:</b> {data['first_name']}\n"
#             f"<b>Birthdate:</b> {data['birthdate']}\n"
#             f"<b>Age:</b> {data['age']}\n")
#     await message.answer_photo(data['image'], caption=text)
#
#
# @dp.message(CommandStart())
# async def command_start(message: Message, state: FSMContext) -> None:
#     await state.set_state(Form.first_name)
#     await message.answer('Xush kelibsiz !')
#     await message.answer('Ismizni kiriting:')

#
# districts_csv = "districts.csv"
# regions_csv = "regions.csv"
# districts_json = "districts.json"
# regions_json = "regions.json"
#
# with open(districts_csv, encoding='utf-8-sig') as csvfile:
#     reader = csv.DictReader(csvfile)
#     rows = list(reader)
#
# with open(districts_json, 'w', encoding='utf-8') as jsonfile:
#     json.dump(rows, jsonfile, indent=4, ensure_ascii=False)
#
# with open(regions_csv, newline='', encoding='utf-8-sig') as csvfile:
#     reader = csv.DictReader(csvfile)
#     rows = list(reader)
#
# with open(regions_json, 'w', encoding='utf-8') as jsonfile:
#     json.dump(rows, jsonfile, indent=4, ensure_ascii=False)
@dp.message(Command("migrate"))
async def migrate_command_handler(message: Message):
    with open('districts.csv', encoding='utf-8-sig') as d_file, open('regions.csv', encoding='utf-8-sig') as r_file:
        regions = DictReader(r_file)
        district = DictReader(d_file)
        for i in regions:
            data = {
                "id": int(i['id']),
                "name": i['name']
            }
            Region.create(**data)
        for i in district:
            data = {
                "id": int(i['id']),
                "name": i['name'],
                "region_id": i["region_id"]
            }
            District.create(**data)
    await message.answer("Viloyat va tumanlar muvaffaqiyatli qo'shildi!✅")


@dp.message(CommandStart())
async def start(message: Message) -> None:
    await message.answer("Botga xush kelibsiz😊 ")
    regions = Region.get_all()
    ikm = InlineKeyboardBuilder()
    for region in regions:
        ikm.add(InlineKeyboardButton(text=region.name, callback_data=f"category:{region.id}"))
    ikm.adjust(1)
    await message.answer("Viloyatlar:", reply_markup=ikm.as_markup())

@dp.callback_query(F.data.startswith(f"region:{'region:'}"))
async def category_filter(callback: CallbackQuery):
    region_id = callback.data.removeprefix('region:')
    ikm = InlineKeyboardBuilder()
    districts = District.filter(region_id=region_id)
    for district in districts:
        ikm.add(InlineKeyboardButton(text=district.name, callback_data=f"district:{district.id}"))
    ikm.adjust(1)

    await callback.message.edit_reply_markup(callback.inline_message_id,ikm.as_markup())

@dp.callback_query(F.data.startswith('district:'))
async def district_filter(callback: CallbackQuery):
    msg = callback.data.removeprefix('district:')
    await callback.message.answer(msg + "malumotlarni chiqarish kerak")
    await callback.answer('')


async def main() -> None:
    bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    # dp.startup.register(startup)
    # dp.shutdown.register(shutdown)
    await dp.start_polling(bot)


if names() == "main":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
