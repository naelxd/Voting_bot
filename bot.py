#!venv/bin/python
# -*- encoding: utf-8 -*-
import logging

import geopy.distance as geo
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.executor import start_webhook

import config

WEBHOOK_HOST = 'https://pmpu.site'
WEBHOOK_PATH = '/lecTop/'
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

WEBAPP_HOST = '127.0.0.1'
WEBAPP_PORT = 7787

bot = Bot(token=config.TOKEN)

storage = MemoryStorage()
# Диспетчер для бота
dp = Dispatcher(bot, storage=storage)
# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)


async def on_startup(dp):
    await bot.set_webhook(WEBHOOK_URL)


async def on_shutdown(dp):
    await bot.delete_webhook()


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

org_loc = (org_loc1, org_loc2)


class Form(StatesGroup):
    geo = State()
    answer = State()
    log = State()


@dp.callback_query_handler(text="first", state=Form.answer)
async def vote1(call: types.CallbackQuery):
    result[0] += 1
    await call.answer(text="Спасибо за участие в нашем мероприятии! Ждем всех 29 апреля на Campus Fest!",
                      show_alert=True)
    await Form.next()


@dp.callback_query_handler(text="second", state=Form.answer)
async def vote2(call: types.CallbackQuery):
    result[1] += 1
    await call.answer(text="Спасибо за участие в нашем мероприятии! Ждем всех 29 апреля на Campus Fest!",
                      show_alert=True)
    await Form.next()


@dp.callback_query_handler(text="third", state=Form.answer)
async def vote3(call: types.CallbackQuery):
    result[2] += 1
    await call.answer(text="Спасибо за участие в нашем мероприятии! Ждем всех 29 апреля на Campus Fest!",
                      show_alert=True)
    await Form.next()


@dp.message_handler(commands="admin", state='*')
async def admin_start(message: types.Message):
    return await Form.geo.set()


@dp.message_handler(lambda message: 'Baltic Eagles' in message.text, state=Form.geo)
async def admin_check(message: types.Message):
    global org_loc
    if "1" in message.text:
        org_loc = (org_loc1, org_loc2)
    elif "2" in message.text:
        org_loc = (org_loc3, org_loc4)
    elif "3" in message.text:
        org_loc = (org_loc5, org_loc6)
    return await Form.next()


@dp.message_handler(lambda message: message.text == 'Check', state=Form.answer)
async def admin_res(message: types.Message, state: FSMContext):
    await state.finish()
    return await message.answer(", ".join(str(x) for x in result))


@dp.message_handler(lambda message: message.text == 'Finish', state=Form.answer)
async def admin_finish(message: types.Message, state: FSMContext):
    await state.finish()
    names = ['ZeЧипсы', 'Совиная голова', 'Прятки']
    ans = dict()
    for i in range(len(names)):
        ans[names[i]] = result[i]
    ans = dict(sorted(ans.items(), key=lambda item: item[1], reverse=True))
    return await message.answer(str(ans))


@dp.message_handler(commands="start")
async def start(message: types.Message):
    await Form.geo.set()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton(text="Поделиться геолокацией", request_location=True))
    await message.answer(
        "Добрый вечер! Здесь вы сможете оставить свой голос за самого понравившегося артиста! Вам необходимо поделиться геолокацией, чтобы мы могли проверить, что вы находитесь сейчас с нами в клубе",
        reply_markup=keyboard)


@dp.message_handler(content_types=['location'], state=Form.geo)
async def geo_start(msg: types.Message):
    print(msg.location)
    lat = msg.location.latitude
    lon = msg.location.longitude
    people_loc = (lat, lon)
    if geo.geodesic(org_loc, people_loc).m < 300:
        await Form.next()
        await msg.reply("Вы допущены к голосованию!",
                        reply_markup=types.ReplyKeyboardRemove())
        await voting(msg)
        print(result)
    else:
        return await msg.answer("Вы находитесь слишком далеко от клуба! Вы можете попробовать снова.")


# @dp.message_handler(state='*', commands='cancel')
# @dp.message_handler(Text(equals='отмена', ignore_case=True), state='*')
# async def cancel_handler(message: types.Message, state: FSMContext):
#     await state.finish()
#     await message.reply('ОК, \cancel так \cancel. Можешь начать сначала написав /start!')

@dp.message_handler(state=Form.answer)
async def voting(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="ZeЧипсы", callback_data="first")).add(
        types.InlineKeyboardButton(text="Совиная голова", callback_data="second")).add(
        types.InlineKeyboardButton(text="Прятки", callback_data="third"))
    await message.answer("Оставьте ваш голос!", reply_markup=keyboard)


if __name__ == "__main__":
    # Запуск бота
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )
