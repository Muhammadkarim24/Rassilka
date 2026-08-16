import csv
import os
from pathlib import Path
from aiogram import Bot, Dispatcher, F, Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command, CommandStart
from ras_api_token import BOT_TOKEN, ADMIN_ID
from aiogram.enums.chat_member_status import ChatMemberStatus
import config
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.fsm.storage.memory import MemoryStorage

#Настройка

USERS_CSV = Path("users.csv") 

PROXY_URL = os.getenv("BOT_PROXY")
_session = AiohttpSession(proxy=PROXY_URL) if PROXY_URL else None

bot = Bot(token=BOT_TOKEN, session=_session)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

scheduler = AsyncIOScheduler(timezone="Europe/Moscow")

user_router = Router()




def get_channels_keyboard():
    keyboard = []
    for username in config.sponsors:
        keyboard.append([InlineKeyboardButton(
            text = f"Перейти:@{username}",
            url= f"https://t.me/{username}"
        )])

    keyboard.append([InlineKeyboardButton(text= "Проверить подписку", callback_data="check_subs")]) 
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
    

#Check subscripbion
async def is_user_subscribed(user_id: int) -> bool:
    for channel in config.sponsors:
        
        member= await bot.get_chat_member(chat_id=-1004380577712,  user_id= user_id)
        if member.status not in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]:
            return False
    return True    




#Хранение пользователей в csv

def add_user(user_id: int):
    users = get_all_users()
    if user_id not in users:
        with open(USERS_CSV, "a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([user_id])
def get_all_users() -> list[int]:
    if not USERS_CSV.exists():
        return[]
    with open(USERS_CSV, "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        return [int(row[0]) for row in reader if row]

#Keyboard

def admin_main_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text ="Статистика", callback_data="stats")],
        [InlineKeyboardButton(text= "Список пользователей", callback_data="users")],
        [InlineKeyboardButton(text= "Распространить", callback_data="broadcast")],
    ])    

def back_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Назад", callback_data="back_to_admin")]
    ])
def admin_button():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Админ", callback_data="open_admin")]
    ])



#Start
@dp.message(CommandStart())
async def start_handler(message: Message):
    await message.answer(
        "Для доступа к боту, подпишитесь на каналы:",
        reply_markup=get_channels_keyboard()
    )

#Obrabotka check_button
@dp.callback_query(F.data=="check_subs")
async def check_subscription(callback: CallbackQuery):
    is_subscribed = await is_user_subscribed(callback.from_user.id)
    if is_subscribed:
        await callback.message.edit_text("Подписка проверена. Доступ разрешен!")    
        await callback.message.answer(f"Для запуска бота напишите /run! \n\n")
    else:
        await callback.answer("Вы не подписались на все каналы!", show_alert=True)



#/start###

@dp.message(Command("run"))
async def start_handler(message: Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("Салом, Админ!", reply_markup= admin_button())
    else:
        await message.answer("Салом! Я бот. \nДанный момент не могу вам ответить!")



#Админ-панель

@dp.message(Command("admin"))
async def open_admin(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer("Панель админа", reply_markup=admin_main_kb())

@dp.callback_query(lambda c: c.data == "open_admin")
async def open_admin(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    await callback.message.answer("Панель админа", reply_markup=admin_main_kb())


@dp.callback_query(lambda c: c.data == "back_to_admin")
async def open_admin(callback: CallbackQuery):
    await callback.message.edit_text("Панель админа", reply_markup=admin_main_kb())



@dp.callback_query(lambda c: c.data == "stats")
async def start_handler(callback: CallbackQuery):
    users = get_all_users()
    text = f"Колличество пользователей: {len(users)}\n"
    if users:
        text += f'Последний: {users[-1]}'
    await callback.message.edit_text(text, reply_markup= back_kb())


#Список пользователей

@dp.callback_query(lambda c: c.data =="users")
async def user_handler(callback: CallbackQuery):
    users = get_all_users()
    if not users:
        await callback.message.edit_text("Пока нет пользователей!", reply_markup=back_kb())
        return
    kb = InlineKeyboardMarkup(inline_keyboard = [
    [InlineKeyboardButton(text=str(uid), url =f"tg://user?id={uid}")]
    for uid in users
    ])
    kb.inline_keyboard.append([InlineKeyboardButton(text = "Назад", callback_data="back_to_admin")])
    await callback.message.edit_text("Список пользователей:", reply_markup=kb)


#Начало рассылки

broadcast_cache = {}

def cancel_btn_kb():
    return InlineKeyboardMarkup(inline_keyboard= [
        [InlineKeyboardButton(text="Отключить кнопку!", callback_data="cancel_button")]
    ])

def confirm_kb():
    return InlineKeyboardMarkup(inline_keyboard= [
        [InlineKeyboardButton(text="Отправить", callback_data="confirm_broadcast")],
        [InlineKeyboardButton(text="Отключить", callback_data="cancel_broadcast")]
    ])


@dp.callback_query(lambda c: c.data=="broadcast")
async def broadcast_start(callback: CallbackQuery):
    await callback.message.answer("Отправьте письмо(текст, изображение, видео, голос, документ) для рассылки:")
    broadcast_cache[callback.from_user.id] = {"msg": None, "btn_text": None, "btn_url": None, "stage": "wait_msg" } 

@dp.message()
async def broadcast_flow(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    state = broadcast_cache.get(ADMIN_ID) 

    if state and state["stage"] == "wait_msg":
        state["msg"] = message
        state["stage"] = "wait_btn_text"
        await message.answer(
            "Если хотите добавить кнопку,\n"
            "Если не хотите, то отправьте!",
            reply_markup= cancel_btn_kb()
        )
        return    
    if state and state["stage"] == "wait_btn_text":
        state["btn_text"] = message.text 
        state["stage"] = "wait_btn_url"
        await message.answer(
            "Теперь присылайте (URL) для кнопки!\n"
            "Или, если не хотите,",
            reply_markup=cancel_btn_kb()
        )
        return 
    if state and state["stage"] == "wait_btn_url":
        state["btn_url"] = message.text
        state["stage"] = "preview"
        #ставим кнопки если есть
        kb = None
        if state["btn_text"] and state["btn_url"]:
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=state["btn_text"], url= state["btn_url"])]
            ])


        msg = state["msg"] 
        if msg.text: 
            await message.answer(msg.text, reply_markup=kb)
        elif msg.photo:
            await message.answer(msg.photo[-1].file_id, caption = msg.caption or "",  reply_markup=kb)              
        elif msg.video:
            await message.answer(msg.video.file_id, caption = msg.caption or "",  reply_markup=kb)
        elif msg.voice:
            await message.answer(msg.voice.file_id, caption = msg.caption or "",  reply_markup=kb)
        elif msg.document:
            await message.answer(msg.document.file_id, caption = msg.caption or "",  reply_markup=kb)
        await message.answer("Хотите ли отправить письмо?", reply_markup=confirm_kb())
        return                                       

#Кнопка отмены

@dp.callback_query(lambda c: c.data== "cancel_button")
async def cancel_button(callback: CallbackQuery):
    state = broadcast_cache.get(ADMIN_ID)
    if not state:
        return
    state["btn_text"], state["btn_url"] = None, None
    state["stage"] = "preview"

    msg = state["msg"]
    if msg.text: 
        await callback.message.answer(msg.text)
    elif msg.photo:
        await callback.message.answer(msg.photo[-1].file_id, caption = msg.caption or "")              
    elif msg.photo:
        await callback.message.answer(msg.video.file_id, caption = msg.caption or "")
    elif msg.photo:
        await callback.message.answer(msg.voice.file_id, caption = msg.caption or "")
    elif msg.photo:
        await callback.message.answer(msg.document.file_id, caption = msg.caption or "")
        await callback.message.answer("Хотите ли отправить письмо?", reply_markup=confirm_kb())
    return               

#Кнопка подтверждения/отмена

@dp.callback_query(lambda c: c.data == "confirm_broadcast")
async def confirm_broadcast(callback: CallbackQuery):
    state = broadcast_cache.get(ADMIN_ID)
    if not state or not state["msg"]:
        await callback.message.edit_text("Ошибка. Письмо не существует!")
        return

    users = get_all_users()
    sent, failed = 0, 0

    kb = None
    if state["btn_text"] and state["btn_url"]:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=state["btn_text"], url=state["btn_url"])]
        ])

    msg = state["msg"]
    for uid in users:
        try:
            if msg.text:
                await bot.send_message(uid, msg.text, reply_markup=kb)
            elif msg.photo:
                await bot.send_photo(uid, msg.photo[-1].file_id, caption=msg.caption or "", reply_markup=kb)
            elif msg.video:
                await bot.send_video(uid, msg.video.file_id, caption=msg.caption or "", reply_markup=kb)
            elif msg.voice:
                await bot.send_voice(uid, msg.voice.file_id, caption=msg.caption or "", reply_markup=kb)
            elif msg.document:
                await bot.send_document(uid, msg.document.file_id, caption=msg.caption or "", reply_markup=kb)
            sent += 1
        except Exception:
            failed += 1

    broadcast_cache[ADMIN_ID] = None
    await callback.message.edit_text(f"Отправлено: {sent}\nОшибки: {failed}")

@dp.callback_query(lambda c: c.data == "cancel_broadcast")
async def cancel_broadcast(callback: CallbackQuery):
    broadcast_cache[ADMIN_ID] = None
    await callback.message.edit_text("Рассылка отклонено!")


#Запуск

if __name__ == "__main__":
    import asyncio
    print('Bot started')
    asyncio.run(dp.start_polling(bot))
    print(222)




    