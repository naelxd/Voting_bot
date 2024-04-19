# python3.11
import logging
import asyncio

import geopy.distance as geo
from aiogram import F
from aiogram import Bot, Dispatcher, types, Router
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command, CommandStart
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder

import config


form_router = Router()

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()
dp.include_router(form_router)


# Zocollo
org_loc1 = 59.925369
org_loc2 = 30.361873
# PUNK
org_loc3 = 59.875778
org_loc4 = 29.825936
# AMCP
org_loc5 = 59.881671
org_loc6 = 29.830563

org_loc7, org_loc8 = 59.87341478785189, 29.827494102129958

org_loc = (org_loc7, org_loc8)

bands_nom1 = [
        "куросио (Шемякин Лев)",
        "Ринат",
        "сам по себе (Дима)",
        "Колизей (Оля Вагапова, Костя Богданов, Дима Бедяев)",
        "Не я первый, не я последний или просто Дима Кривошей (Дима Кривошей)",
        "Самуил Налисин и Юлия Габелко",
        "Самуил Налисин",
        "поля и алиса (Полина Золотухина и Алиса Никифорова)",
        "скайрекс (Никита Измайлов)",
        "поля и алиса (Полина Золотухина и Алиса Никифорова)",
        ]

bands_nom2 = [
        "куросио (Шемякин Лев)",
        "Ринат",
        "сам по себе (Дима)",
        "Ксения Андреевна (Ксения Костерова)",
        "Колизей (Оля Вагапова, Костя Богданов, Дима Бедяев)",
        "Не я первый, не я последний или просто Дима Кривошей (Дима Кривошей)",
        "Самуил Налисин и Юлия Габелко",
        "Самуил Налисин",
        "поля и алиса (Полина Золотухина и Алиса Никифорова)",
        "скайрекс (Никита Измайлов)",
        "поля и алиса (Полина Золотухина и Алиса Никифорова)",
        ]

bands_nom3 = [
        "куросио (Шемякин Лев)",
        "Ринат",
        "сам по себе (Дима)",
        "Ксения Андреевна (Ксения Костерова)",
        "Колизей (Оля Вагапова, Костя Богданов, Дима Бедяев)",
        "Не я первый, не я последний или просто Дима Кривошей (Дима Кривошей)",
        "Самуил Налисин и Юлия Габелко",
        "Самуил Налисин",
        "поля и алиса (Полина Золотухина и Алиса Никифорова)",
        "скайрекс (Никита Измайлов)",
        "поля и алиса (Полина Золотухина и Алиса Никифорова)",
        ]

result = {
        "Лучший вокал": [0]*len(bands_nom1),
        "Лучший инструментал": [0]*len(bands_nom2),
        "Лучшее выступление": [0]*len(bands_nom3),
        }


class Form(StatesGroup):
    geo = State()
    answer = State()
    nom1 = State()
    nom2 = State()
    nom3 = State()
    log = State()


@form_router.message(CommandStart())
async def start(message: types.Message, state: FSMContext):
    await state.set_state(Form.geo)
    keyboard = types.ReplyKeyboardMarkup(
            keyboard=[
                [types.KeyboardButton(text="Поделиться геолокацией",
                                      request_location=True)]
                ], 
            resize_keyboard=True)
    await message.answer(
        "Добрый вечер! Здесь вы сможете оставить свой голос за самого понравившегося артиста! Вам необходимо поделиться геолокацией, чтобы мы могли проверить, что вы находитесь сейчас с нами в клубе",
        reply_markup=keyboard)


@form_router.message(Form.geo)
async def geo_start(msg: types.Message, state: FSMContext):
    print(msg.location)
    lat = msg.location.latitude
    lon = msg.location.longitude
    people_loc = (lat, lon)
    if geo.geodesic(org_loc, people_loc).m < 300:
        await state.set_state(Form.nom1)
        await msg.answer("Вы допущены к голосованию! В голосовании будет 3 номинации: лучший вокал, лучший инструментал, лучшее выступление. Выбирай внимательно",
                        reply_markup=types.ReplyKeyboardRemove())
        keyboard = types.ReplyKeyboardMarkup(
                keyboard=[
                    [types.KeyboardButton(text=bands_nom1[band_ind])]
                    for band_ind in range(len(bands_nom1))
                ],
                resize_keyboard=True
                )
        await msg.answer(text="Выбери лучший вокал",
                        reply_markup=keyboard)
    else:
        return await msg.answer("Вы находитесь слишком далеко от клуба! Вы можете попробовать снова.")


@form_router.message(Form.nom1)
async def nom1_answer(msg: types.Message, state: FSMContext):
    if msg.text in bands_nom1:
        result["Лучший вокал"][bands_nom1.index(msg.text)] += 1
        keyboard = types.ReplyKeyboardMarkup(
                keyboard=[
                    [types.KeyboardButton(text=band)]
                    for band in bands_nom2
                ],
                resize_keyboard=True
                )
        await state.set_state(Form.nom2)
        await msg.answer("Выбери лучший инструментал", reply_markup=keyboard)
    else:
        await msg.reply("не понял")


@form_router.message(Form.nom2)
async def nom1_answer(msg: types.Message, state: FSMContext):
    if msg.text in bands_nom2:
        result["Лучший инструментал"][bands_nom2.index(msg.text)] += 1
        keyboard = types.ReplyKeyboardMarkup(
                keyboard=[
                    [types.KeyboardButton(text=band)]
                    for band in bands_nom3
                ],
                resize_keyboard=True
                )
        await state.set_state(Form.nom3)
        await msg.answer("Выбери лучшее выступление", reply_markup=keyboard)
    else:
        await msg.reply("не понял")


@form_router.message(Form.nom3)
async def nom1_answer(msg: types.Message, state: FSMContext):
    if msg.text in bands_nom3:
        result["Лучшее выступление"][bands_nom3.index(msg.text)] += 1
        await state.set_state(Form.log)
        await msg.answer("Спасибо за участие!")
        print(result)
    else:
        await msg.reply("не понял")


@form_router.message(Command("biba"))
async def biba_comm(msg: types.Message, state: FSMContext):
    message = ""
    message += f"Лучший вокал:\n"
    ind = max(range(len(result['Лучший вокал'])), key=lambda x : result['Лучший вокал'][x])
    message += f"{bands_nom1[ind]} \n{result['Лучший вокал'][ind]} голосов"
    message += '\n'
    message += f"Лучший инструментал:\n"
    ind = max(range(len(result['Лучший инструментал'])), key=lambda x : result['Лучший инструментал'][x])
    message += f"{bands_nom1[ind]} \n{result['Лучший инструментал'][ind]} голосов"
    message += '\n'
    message += f"Лучшее выступление:\n"
    ind = max(range(len(result['Лучшее выступление'])), key=lambda x : result['Лучшее выступление'][x])
    message += f"{bands_nom1[ind]} \n{result['Лучшее выступление'][ind]} голосов"

    await msg.answer(message)


@form_router.message(Command("bibaall"))
async def biba_all(msg: types.Message, state: FSMContext):
    message = ""
    message += f"*Лучший вокал:*\n"
    for ind in range(len(result["Лучший вокал"])):
        message += f"{bands_nom1[ind]} \n*{result['Лучший вокал'][ind]}* голосов\n"
    message += "\n"

    message += f"*Лучший инструментал:*\n"
    for ind in range(len(result["Лучший инструментал"])):
        message += f"{bands_nom2[ind]} \n*{result['Лучший инструментал'][ind]}* голосов\n"
    message += "\n"

    message += f"*Лучшее выступление:*\n"
    for ind in range(len(result["Лучшее выступление"])):
        message += f"{bands_nom3[ind]} \n*{result['Лучшее выступление'][ind]}* голосов\n"

    await msg.answer(message, parse_mode="Markdown")
    

async def main():

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
