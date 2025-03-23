import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from datetime import datetime, timedelta

TOKEN = "7686264861:AAGeTBdN-x4sJ4jQmdUJQ3JbLyrZgS1E1D8"
ADMIN_ID = 8152258436  # Bitta admin ID
CARD_INFO = "💳 Toʻlov kartalari:\n\n💰 Uzcard: 5614 6821 1877 7673\n💰 Humo: 9860 1701 1178 5060\n💰 Click/Payme: Xozircha faol emas"

session = AiohttpSession()
from aiogram.client.default import DefaultBotProperties

bot = Bot(token=TOKEN, session=session, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

users = {}
pending_payments = {}

main_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Premium Narxlar", callback_data="prices")],
    [InlineKeyboardButton(text="Toʻlov qilish", callback_data="payment")],
    [InlineKeyboardButton(text="Profilim", callback_data="profile")]
])

payment_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Toʻlov cheki yuborish", callback_data="send_receipt")],
    [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back")]
])

prices_text = "📌 Premium narxlar:\n\n1️⃣ 1 oylik - 40 000 so'm\n2️⃣ 3 oylik - 180 000 so'm\n3️⃣ 6 oylik - 220 000 so'm\n4️⃣ 12 oylik - 400 000 so'm"

payment_options = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="1 oylik", callback_data="pay_1m")],
    [InlineKeyboardButton(text="3 oylik", callback_data="pay_3m")],
    [InlineKeyboardButton(text="6 oylik", callback_data="pay_6m")],
    [InlineKeyboardButton(text="12 oylik", callback_data="pay_12m")],
    [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back")]
])

@dp.message(F.text == "/start")
async def start(message: types.Message):
    await message.answer(f"Assalomu alaykum {message.from_user.full_name}! \n\nBotimiz orqali premium sotib olishingiz mumkin.", reply_markup=main_menu)

@dp.callback_query(F.data == "prices")
async def show_prices(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text(prices_text, reply_markup=main_menu)

@dp.callback_query(F.data == "payment")
async def ask_payment_duration(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text("Nechchi oylik premium sotib olmoqchisiz?", reply_markup=payment_options)

@dp.callback_query(F.data.startswith("pay_"))
async def select_payment(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    user_name = callback_query.from_user.full_name
    duration = int(callback_query.data.split("_")[1][0])
    pending_payments[user_id] = duration
    await bot.send_message(user_id, f"{CARD_INFO}\n\nToʻlovni amalga oshiring va chekni botga yuboring.")

@dp.callback_query(F.data == "send_receipt")
async def request_receipt(callback_query: types.CallbackQuery):
    await callback_query.message.answer("Iltimos, toʻlov chekini rasm yoki hujjat sifatida yuboring.")

@dp.message(F.photo | F.document)
async def receive_receipt(message: types.Message):
    user_id = message.from_user.id
    user_name = message.from_user.full_name
    username = message.from_user.username or "@unknown"
    if user_id in pending_payments:
        duration = pending_payments[user_id]
        caption_text = f"👤 Ism: {user_name}\n🆔 ID: {user_id}\n💬 Username: {username}\n🛒 {duration} oylik premium \n✅ Tasdiqlaysizmi?"
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"confirm_{user_id}_{duration}")],
            [InlineKeyboardButton(text="❌ Rad etish", callback_data=f"decline_{user_id}")]
        ])
        if message.photo:
            await bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=caption_text, reply_markup=markup)
        elif message.document:
            await bot.send_document(ADMIN_ID, message.document.file_id, caption=caption_text, reply_markup=markup)
        await message.answer("Toʻlov tasdiqlanishini kuting.")
    else:
        await message.answer("Siz hali toʻlov variantini tanlamagansiz.")

@dp.callback_query(F.data.startswith("confirm_"))
async def confirm_payment(callback_query: types.CallbackQuery):
    _, user_id, duration = callback_query.data.split("_")
    user_id, duration = int(user_id), int(duration)
    expire_date = datetime.now() + timedelta(days=30 * duration)
    users[user_id] = expire_date
    await bot.send_message(user_id, f"✅ Toʻlov tasdiqlandi! Premium muddati: {expire_date.strftime('%Y-%m-%d')}")
    await callback_query.answer("Toʻlov tasdiqlandi.", show_alert=True)

@dp.callback_query(F.data.startswith("decline_"))
async def decline_payment(callback_query: types.CallbackQuery):
    user_id = int(callback_query.data.split("_")[1])
    await bot.send_message(user_id, "❌ Toʻlovingiz rad etildi. Iltimos, qayta urinib ko‘ring.")
    await callback_query.answer("Toʻlov rad etildi.", show_alert=True)

@dp.callback_query(F.data == "profile")
async def show_profile(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    user_name = callback_query.from_user.full_name
    premium_info = "Sizda premium yoʻq!" if user_id not in users else f"📅 Premium muddati: {users[user_id].strftime('%Y-%m-%d')}"
    profile_text = f"👤 Ism: {user_name}\n🆔 ID: {user_id}\n{premium_info}"
    await callback_query.message.edit_text(profile_text, reply_markup=main_menu)

@dp.callback_query(F.data == "back")
async def go_back(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text("Siz asosiy menyudasiz.", reply_markup=main_menu)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
