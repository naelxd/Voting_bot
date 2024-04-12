# python3.11
import logging
import asyncio

import geopy.distance as geo
from aiogram import Bot, Dispatcher, types, Router
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command, CommandStart

import config


form_router = Router()

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)


# Zocollo
org_loc1 = 59.925369
org_loc2 = 30.361873
# PUNK
org_loc3 = 59.875778
org_loc4 = 29.825936
# AMCP
org_loc5 = 59.881671
org_loc6 = 29.830563
result = [0, 0, 0]

org_loc = (org_loc3, org_loc4)

bands = [
        "Группа 1",
        "Группа 2",
        "Группа 3",
        ]

result = {
        "Лучший вокал": [0]*len(bands),
        "Лучший инструментал": [0]*len(bands),
        "Лучшее выступление": [0]*len(bands),
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
        await msg.answer("Вы допущены к голосованию! В голосовании будет 3 номинации: лучший вокал, лучший инструментал, лучшее выступление. Выбирай внимаетльно",
                        reply_markup=types.ReplyKeyboardRemove())
        keyboard = types.ReplyKeyboardMarkup(
                keyboard=[
                    [types.KeyboardButton(text=band) for band in bands]
                ],
                resize_keyboard=True
                )
        await msg.answer("Выбери лучший вокал",
                        reply_markup=keyboard)
    else:
        return await msg.answer("Вы находитесь слишком далеко от клуба! Вы можете попробовать снова.")


@form_router.message(Form.nom1)
async def nom1_answer(msg: types.Message, state: FSMContext):
    if msg.text in bands:
        result["Лучший вокал"][bands.index(msg.text)] += 1
        await state.set_state(Form.nom2)
        await msg.answer("Выбери лучший инструментал")
    else:
        await msg.reply("не понял")


@form_router.message(Form.nom2)
async def nom1_answer(msg: types.Message, state: FSMContext):
    if msg.text in bands:
        result["Лучший инструментал"][bands.index(msg.text)] += 1
        await state.set_state(Form.nom3)
        await msg.answer("Выбери лучшее выступление")
    else:
        await msg.reply("не понял")


@form_router.message(Form.nom3)
async def nom1_answer(msg: types.Message, state: FSMContext):
    if msg.text in bands:
        result["Лучшее выступление"][bands.index(msg.text)] += 1
        await state.set_state(Form.log)
        await msg.answer("Спасибо за участие!")
        print(result)
    else:
        await msg.reply("не понял")


@form_router.message(Command("biba"))
async def nom1_answer(msg: types.Message, state: FSMContext):
    message = ""
    for key in result:
        message += f"{key}:\n"
        for band_ind in range(len(bands)):
            message += f"-{bands[band_ind]} {result[key][band_ind]} голосов\n"

    await msg.answer(message)
    

async def main():
    bot = Bot(token=config.TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher()
    dp.include_router(form_router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    # Запуск бота
    # start_webhook(
    #     dispatcher=dp,
    #     webhook_path=WEBHOOK_PATH,
    #     on_startup=on_startup,
    #     on_shutdown=on_shutdown,
    #     skip_updates=True,
    #     host=WEBAPP_HOST,
    #     port=WEBAPP_PORT,
    # )
    asyncio.run(main())
    
