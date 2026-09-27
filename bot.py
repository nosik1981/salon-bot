import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

TOKEN = "8941088978:AAGnN14TGxTjeG8da0ovOV0md3noEO603tU"

bot = Bot(token=TOKEN)
dp = Dispatcher()

SERVICES = [
    {"name": "💅 Маникюр", "price": 2000, "desc": "Классический маникюр с покрытием"},
    {"name": "🦶 Педикюр", "price": 2500, "desc": "Аппаратный педикюр с уходом"},
    {"name": "✂️ Женская стрижка", "price": 1500, "desc": "Стрижка с укладкой"},
    {"name": "✂️ Мужская стрижка", "price": 1200, "desc": "Классическая мужская стрижка"},
    {"name": "🎨 Окрашивание волос", "price": 3000, "desc": "Окрашивание в один тон или мелирование"},
    {"name": "👁️ Коррекция бровей", "price": 800, "desc": "Коррекция формы и окрашивание"},
    {"name": "👁️ Наращивание ресниц", "price": 2500, "desc": "Классика, 2D, 3D"},
    {"name": "🧖 Чистка лица", "price": 3000, "desc": "Ультразвуковая или механическая"},
    {"name": "💆 Массаж лица", "price": 2000, "desc": "Расслабляющий массаж лица"},
    {"name": "💆‍♂️ Классический массаж", "price": 2500, "desc": "Общий массаж тела"},
    {"name": "🧘 Расслабляющий массаж", "price": 3000, "desc": "Массаж с аромамаслами"},
    {"name": "🛁 СПА-ритуал", "price": 5000, "desc": "Комплексная программа для тела"},
    {"name": "🌿 Обёртывание", "price": 2500, "desc": "Водорослевое, грязевое или шоколадное"},
]

ADMIN_ID = 644259377


class BookingStates(StatesGroup):
    choosing_service = State()
    entering_name = State()
    entering_phone = State()


def main_menu():
    builder = ReplyKeyboardBuilder()
    builder.button(text="💅 Услуги")
    builder.button(text="📝 Записаться")
    builder.button(text="📞 Контакты")
    return builder.as_markup(resize_keyboard=True)


@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer(
        "Привет! Я демо-бот для салона красоты. Чем могу помочь?",
        reply_markup=main_menu()
    )


@dp.message(F.text == "💅 Услуги")
async def services_handler(message: types.Message):
    for service in SERVICES:
        await message.answer(
            f"{service['name']}\n\n{service['desc']}\n\n💰 Цена: {service['price']} ₽"
        )


@dp.message(F.text == "📞 Контакты")
async def contacts_handler(message: types.Message):
    await message.answer(
        "📍 Адрес: ул. Примерная, 1\n📞 Телефон: +7 700 000 00 00\n🕐 Работаем: 9:00–21:00"
    )


@dp.message(F.text == "📝 Записаться")
async def booking_start(message: types.Message, state: FSMContext):
    builder = InlineKeyboardBuilder()
    for i, service in enumerate(SERVICES):
        builder.button(text=f"{service['name']} — {service['price']} ₽", callback_data=f"book_{i}")
    builder.adjust(1)
    await message.answer("Выберите услугу:", reply_markup=builder.as_markup())
    await state.set_state(BookingStates.choosing_service)


@dp.callback_query(F.data.startswith("book_"), BookingStates.choosing_service)
async def booking_service(callback: types.CallbackQuery, state: FSMContext):
    index = int(callback.data.split("_")[1])
    service = SERVICES[index]
    await state.update_data(service=service["name"], price=service["price"])
    await callback.message.answer("Введите ваше имя:")
    await state.set_state(BookingStates.entering_name)
    await callback.answer()


@dp.message(BookingStates.entering_name)
async def booking_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите ваш телефон:")
    await state.set_state(BookingStates.entering_phone)


@dp.message(BookingStates.entering_phone)
async def booking_phone(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await state.update_data(phone=message.text)

    if ADMIN_ID != 0:
        await bot.send_message(
            ADMIN_ID,
            f"🔔 Новая запись!\n\n"
            f"Услуга: {data['service']}\n"
            f"Цена: {data['price']} ₽\n"
            f"Имя: {data['name']}\n"
            f"Телефон: {message.text}"
        )

    await message.answer(
        f"Спасибо, {data['name']}! Ваша заявка принята.\n\n"
        f"Услуга: {data['service']}\n"
        f"Мы свяжемся с вами по телефону {message.text} для подтверждения.",
        reply_markup=main_menu()
    )
    await state.clear()


async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)


