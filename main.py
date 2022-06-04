import logging
import random
import sqlite3

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import *

API_TOKEN = "5514329220:AAEx6BbHjgvW4YvJtnV3t83Y3FBYty1d9NQ"
logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dispatcher = Dispatcher(bot)
connection = sqlite3.connect("users.db")
cursor = connection.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS clients(
        userid INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        bill INTEGER,
        balance INTEGER DEFAULT 0,
        debt INTEGER DEFAULT 0
        );""")
data = None


def check_name(name):
    a = cursor.execute("""SELECT name FROM clients""").fetchall()
    names = []
    for el in a:
        names.append(*el)
    if name in names:
        return True
    else:
        return False


@dispatcher.message_handler(commands=["start"])
async def auth(message: types.message):
    await message.answer("Введите ФИО")


@dispatcher.message_handler(text="Да")
async def create_client(message: types.message):
    global data
    cursor.execute("""INSERT INTO clients (name, bill) VALUES(?, ?);""", (data, random.randint(2, 10000001)))
    connection.commit()
    keyboard_markup = ReplyKeyboardMarkup(row_width=1)
    buttons = ["Баланс", "Задолжность", "Счет", "Я все узнал"]
    keyboard_markup.add(*buttons)
    await message.answer("Ваш счет создан, что хотите узнать?", reply_markup=keyboard_markup)


@dispatcher.message_handler(text=["Нет", "Я все узнал"])
async def goodbye(message: types.message):
    keyboard_markup = ReplyKeyboardRemove()
    await message.answer(f"Досвиданья, {data}", reply_markup=keyboard_markup)


@dispatcher.message_handler(text="Баланс")
async def get_balance(message: types.message):
    bal = None
    balance = cursor.execute("""SELECT balance FROM clients WHERE name=?""", (data,)).fetchall()
    for el in balance:
        bal = str(*el)
    await message.answer(f"Ваш баланс: {bal}")


@dispatcher.message_handler(text="Задолжность")
async def get_debt(message: types.message):
    debt = None
    d = cursor.execute("""SELECT debt FROM clients WHERE name=?""", (data,)).fetchall()
    for el in d:
        debt = str(*el)
    await message.answer(f"Ваша задолжность: {debt}")


@dispatcher.message_handler(text="Счет")
async def get_bill(message: types.message):
    bill = None
    b = cursor.execute("""SELECT debt FROM clients WHERE name=?""", (data,)).fetchall()
    for el in b:
        bill = str(*el)
    await message.answer(f"Ваш счет: {bill}")


@dispatcher.message_handler()
async def get_fio(message: types.message):
    global data
    data = message.text
    if check_name(data):
        keyboard_markup = ReplyKeyboardMarkup(row_width=1)
        buttons = ["Баланс", "Задолжность", "Счет", "Я все узнал"]
        keyboard_markup.add(*buttons)
        await message.answer(f"Что хотите узнать, {data}?", reply_markup=keyboard_markup)
    else:
        keyboard_markup = ReplyKeyboardMarkup(row_width=1)
        buttons = ["Да", "Нет"]
        keyboard_markup.add(*buttons)
        await message.answer("Вы не являетесь клиентом банка, хотите создать счет?", reply_markup=keyboard_markup)


if __name__ == "__main__":
    executor.start_polling(dispatcher, skip_updates=True)
