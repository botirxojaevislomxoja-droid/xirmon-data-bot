from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import F
import asyncio
from google_sheets import add_product_to_brand, create_brand_sheet
from config import BOT_TOKEN

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


class ProductForm(StatesGroup):
    brand = State()
    name_uz = State()
    name_ru = State()
    desc_uz = State()
    desc_ru = State()
    photo = State()

@dp.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    await message.answer("🇷🇺 Введите название бренда:")
    await state.set_state(ProductForm.brand)


@dp.message(ProductForm.brand)
async def get_brand(message: types.Message, state: FSMContext):
    brand = message.text.strip()
    create_brand_sheet(brand)
    await state.update_data(brand=brand)
    await message.answer("📸 Отправьте фото продукта:")
    await state.set_state(ProductForm.photo)


@dp.message(ProductForm.photo, F.photo)
async def get_photo(message: types.Message, state: FSMContext):
    photo = message.photo[-1].file_id
    await state.update_data(photo=photo)
    await message.answer("🇺🇿 Mahsulot nomini kiriting:")
    await state.set_state(ProductForm.name_uz)


@dp.message(ProductForm.name_uz)
async def get_name_uz(message: types.Message, state: FSMContext):
    await state.update_data(name_uz=message.text.strip())
    await message.answer("🇷🇺 Введите название продукта:")
    await state.set_state(ProductForm.name_ru)


@dp.message(ProductForm.name_ru)
async def get_name_ru(message: types.Message, state: FSMContext):
    await state.update_data(name_ru=message.text.strip())
    await message.answer("🇺🇿 Mahsulot tavsifini kiriting:")
    await state.set_state(ProductForm.desc_uz)


@dp.message(ProductForm.desc_uz)
async def get_desc_uz(message: types.Message, state: FSMContext):
    await state.update_data(desc_uz=message.text.strip())
    await message.answer("🇷🇺 Введите описание продукта:")
    await state.set_state(ProductForm.desc_ru)


@dp.message(ProductForm.desc_ru)
async def finish(message: types.Message, state: FSMContext):
    data = await state.get_data()
    brand = data.get("brand")

    if not brand:
        await message.answer("⚠️ Brend topilmadi. Iltimos, /start buyrug‘i bilan qayta boshlang.")
        return

    # Ma’lumotlarni Google Sheets’ga yozamiz
    add_product_to_brand(brand, [
        data["photo"], data["name_uz"], data["name_ru"], data["desc_uz"], message.text.strip()
    ])

    # 🔘 Tugmalar menyusi
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="➕ Shu brendga yangi mahsulot qo‘shish")],
            [types.KeyboardButton(text="🔄 Boshqa brendga o‘tish")]
        ],
        resize_keyboard=True
    )

    # ✅ brand nomini qayta saqlab qo‘yamiz (keyingi mahsulot uchun)
    await state.clear()
    await state.update_data(brand=brand)

    await message.answer(
        f"✅ Mahsulot '{data['name_uz']}' brend '{brand}' listiga muvaffaqiyatli qo‘shildi!",
        reply_markup=keyboard
    )


# 🔘 Shu brendga mahsulot qo‘shish
@dp.message(F.text == "➕ Shu brendga yangi mahsulot qo‘shish")
async def add_more_products(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if "brand" not in data:
        await message.answer("⚠️ Brend aniqlanmagan. Iltimos, /start buyrug‘idan boshlang.")
        return
    await message.answer("📸 Yangi mahsulot uchun rasm yuboring:")
    await state.set_state(ProductForm.photo)


# 🔘 Boshqa brendga o‘tish
@dp.message(F.text == "🔄 Boshqa brendga o‘tish")
async def change_brand(message: types.Message, state: FSMContext):
    await message.answer("🇷🇺 Введите название нового бренда:", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(ProductForm.brand)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
