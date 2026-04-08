from aiogram import Router , F
from aiogram.filters import Command,CommandStart
from aiogram.types import Message ,CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder 

from aiogram.fsm.state import State, StatesGroup
import config
from aiogram.filters.callback_data import CallbackData

class support_callback(CallbackData,prefix="supp"):
    chat_id:int
    action:str

support_router=Router()

class chat_support(StatesGroup):
    get_user_message=State()
    get_support_message=State()

@support_router.callback_query(F.data=="sendt_user")
@support_router.callback_query(F.data=="support_state")
async def handle_send_message(call:CallbackQuery,state:FSMContext):
    await call.message.reply(text=f"اهلا {call.from_user.full_name} رجائا ادخل الرسالة المطلوب ارسلها الى الدعم الفني")
    await state.set_state(chat_support.get_user_message)
    
@support_router.message(chat_support.get_user_message)
async def handling_send_message_state(msg:Message,state:FSMContext):
     
    user_message=msg.text
    
    settings_data=config.load_settings()
    support_chat_id=settings_data["supprot_group"]

    if not support_chat_id:
        await msg.answer("خطأ: لم يتم ضبط معرف مجموعة الدعم في الإعدادات.")
        return
    
    builder=InlineKeyboardBuilder()
    builder.button(text=f"اضغط للاجابة على {msg.from_user.full_name}",callback_data=support_callback(action="admin_answer",chat_id=msg.chat.id))

    try:
        await msg.bot.send_message(text=f"المتسخدم: {msg.from_user.full_name} \nالرسالة: {user_message}",chat_id=int(support_chat_id),reply_markup=builder.as_markup())
        await msg.answer(text=f"تم ارسال الرسالة الى الدعم الفني ")
        await state.clear()
    except Exception as e:
        await msg.answer("لا يوجد مجموعة لارسال رسائل الدعم فيها بعد او من الممكن انه حصل اشتباه اثناء تعين معرف المجموعة")
        print(f" Error: {e}")

@support_router.callback_query(support_callback.filter(F.action=="admin_answer"))
async def handel_support_reply(call:CallbackQuery,state:FSMContext,callback_data:support_callback):
    await call.message.answer(text=f"ارسل الرسالة المطلوب ارسالها الى المستخدم ")
    await state.update_data(chat_id=str(callback_data.chat_id))
    await state.set_state(chat_support.get_support_message)

@support_router.message(chat_support.get_support_message)
async def handling_support_reply_state(msg:Message,state:FSMContext):
    
    support_message=msg.text
    data= await state.get_data()
    str_chat_id=data.get("chat_id")
    chat_id=int(str_chat_id)
    
    builder=InlineKeyboardBuilder()
    builder.button(text=f"ارسال رسالة الى الدعم الفني",callback_data="sendt_user")

    await state.clear()

    await msg.bot.send_message(text=f"{support_message}",chat_id=chat_id,reply_markup=builder.as_markup())
    await msg.answer(text=f"تم ارسال الرسالة الى المتسخدم")

