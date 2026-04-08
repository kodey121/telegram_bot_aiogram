from aiogram import Router , F
from aiogram.filters import Command,CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder 
from keyboard import MenuAction

command_router=Router()

@command_router.message(Command("cancel"))
@command_router.message(F.text.casefold()=="cancel")
async def Cancel(message:Message,state:FSMContext):
    current_state= await state.get_state()
    if current_state == None:
        return
    await state.clear()
    await message.answer("the opreation have been Cancelled")

@command_router.message(CommandStart())
async def start_command(message:Message)->None:
    await message.answer(f"Hello {message.from_user.full_name} I am at your service")

@command_router.message(Command("myid"))
async def id_hundle1(msg:Message):
    await msg.answer(text=f"your ip is {msg.from_user.id}")

@command_router.message(Command("group_id"))
async def send_group_id(msg:Message):
    await msg.reply(text=f"{msg.chat.id}")

@command_router.message(Command("help"))
async def help_command(message:Message)->None:
    await message.answer("press /menu to start !")

#keyboard_handler
@command_router.message(Command("mainmenu"))
@command_router.message(Command("menu" ))
@command_router.message(Command("mainMenu"))
async def build_menu(msg: Message):
    builder = InlineKeyboardBuilder()
    
    button_data = MenuAction(action="open", parent_id="NULL").pack()
    
    builder.button(text="📂 القائمة الرئيسية", callback_data=button_data)
    builder.button(text="📩 مراسلة الدعم الفني", callback_data="support_state")
    builder.adjust(2,3)
    await msg.reply(text="اختار خيار  من الأتي:", reply_markup=builder.as_markup())
    


   