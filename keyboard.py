from aiogram import Router , F ,html
from aiogram.filters import Command,CommandStart , CommandObject
from aiogram.types import Message , KeyboardButton ,CallbackQuery ,InlineKeyboardButton,ReplyKeyboardRemove
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from typing import Any
from aiogram.utils.keyboard import InlineKeyboardBuilder , ReplyKeyboardBuilder
import database 
from aiogram.filters.callback_data import CallbackData
import config

utils_router=Router()

class MenuAction(CallbackData, prefix="menu"):
    action: str
    parent_id: str 
class AdminAction(CallbackData, prefix="admin"):
    admin_name: str
    admin_id: str 

class create_button(StatesGroup):
    get_name=State()
class upload_file(StatesGroup):
    get_file_id=State()
    finish=State()
class add_admin(StatesGroup):
    get_admin_id= State()

class add_support_group(StatesGroup):
    get_group_id=State()

@utils_router.message(F.text=="Finish✅")
async def finishing_handling(msg:Message,state:FSMContext):
    await state.clear()
    await msg.answer(text=f"Buttons:",reply_markup=ReplyKeyboardRemove())

@utils_router.callback_query(MenuAction.filter(F.action=="send_admin_list"))
async def handle_send_admin_list(call:CallbackQuery):
    admin_data=database.get_admin_info()
    admin_list=[]
    for admin_id ,admin_name in admin_data:
        admin_list.append(f"{admin_name}:{admin_id}")

    response_text="\n".join(admin_list) if admin_list else "no admin found"

    await call.message.answer(text=(f"admins:\n{response_text}"))
    await call.answer()

@utils_router.callback_query(MenuAction.filter(F.action== "select_supp_group"))
async def selecting_groups_handling(call:CallbackQuery,state:FSMContext):
    await call.message.reply(text=f"please send the group id !note the bot must be in this group")
    await state.set_state(add_support_group.get_group_id) 

@utils_router.message(add_support_group.get_group_id)
async def handle_group_selecting_state(msg:Message,state:FSMContext):
    group_id=msg.text
    config.write_settings("supprot_group",group_id)
    await msg.reply(text=f"the group {group_id} is seted as the support_group")
    await state.clear()

@utils_router.callback_query(MenuAction.filter(F.action== "add_admin"))
async def add_admin_handling(call:CallbackQuery,state:FSMContext):
    await call.message.answer(text="send the id of the user please")
    await state.set_state(add_admin.get_admin_id)

@utils_router.callback_query(MenuAction.filter(F.action== "remove_admin_list"))
async def remove_admin_building_menu(call:CallbackQuery,state:FSMContext,callback_data:MenuAction):
    #build the keyboard instance
    builder=InlineKeyboardBuilder()
    builder.adjust(1,2)
    #fetch admins tuples and make a for in loop for each admin and use the name or id of the admins id as button name
    admin_list=database.get_admin_info()
    
    if admin_list == []:

        await call.message.answer(text=f"there is no any admin yet")

        parnet_id=callback_data.parent_id
        user_id=call.from_user.id
        
        mark_up=build_dynamic_menu(parnet_id,user_id)
        await call.message.answer(text=f"folder:{parnet_id}",reply_markup=mark_up)
    else:
        
        for admin_id,admin_name in admin_list:
            builder.button(text=f"{admin_name}:{admin_id}",callback_data=AdminAction(admin_name=f"{admin_name}",admin_id=str(admin_id)).pack())

        await call.message.answer(text="select admin id to remove",reply_markup=builder.as_markup())
    
        
# 
@utils_router.callback_query(AdminAction.filter())
async def remove_admin_handling(call:CallbackQuery,callback_data:AdminAction):
        
        admin_name=callback_data.admin_name
        admin_id=callback_data.admin_id

        admin_to_remove= admin_id

        admin_ids_list=database.get_admin_ids()
        if admin_to_remove not in admin_ids_list:
            await call.message.answer(text=f"there is no such user called {admin_name}")
        else:
            builder=InlineKeyboardBuilder()
            builder.adjust(1,2)
            #admin removeing 
            database.remove_admin(admin_id)
            await call.message.edit_text(text=f"admin {admin_name} has been removed from the list❌")
            
            #live edting the button changing :

            admin_list=database.get_admin_info()

            for admin_id,admin_name in admin_list:
                builder.button(text=f"{admin_name}:{admin_id}",callback_data=AdminAction(admin_name=f"{admin_name}",admin_id=str(admin_id)).pack())
            # we add this condtion here because if the code tried to edit the the reply markup and it's last mark up that will make a small error 
            if len(admin_ids_list) == 1:
                pass
            else:
                await call.message.edit_reply_markup(reply_markup=builder.as_markup())


@utils_router.message(add_admin.get_admin_id)
async def add_admin_handling_state(msg:Message):
    builder=ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="Finish✅"))
    try:
        admin_id=msg.text
        admin_info= await msg.bot.get_chat(admin_id)
        admin_name=admin_info.full_name

        database.add_admin(admin_id,admin_name)
        await msg.answer(text=f"the admin @{admin_info.username} has been added to the list ✅🤵",reply_markup=builder.as_markup())
    except Exception as e :
        await msg.answer(text=f"user {e} is not found ")

@utils_router.callback_query(MenuAction.filter(F.action== "delete_f"))
async def delete_file_handling(call:CallbackQuery,callback_data:MenuAction):
    parent_id=callback_data.parent_id
    if database.get_files_ids(parent_id) == []:
        await call.message.answer(text=f"لا يوجد اي محاضرات مرفوعة لحذفها")
        await call.answer()
    else:
        database.remove_uploaded_file(parent_id)
        await call.message.answer(text=f"تم مسح جميع المحاضرات ❌")
        await call.answer()

@utils_router.callback_query(MenuAction.filter(F.action== "send_flist"))
async def file_sending_info121(call:CallbackQuery,callback_data:MenuAction):

    parent_id=callback_data.parent_id
    ids=database.get_files_ids(parent_id)

    if ids == None or ids== []:
        await call.message.answer(text="لا يوجد اي ملفات مرفوعة")
    else:
        text=""
        for file_id ,doc_id, doc_name in ids:
            text=(f"ملف رقم {file_id}, اسم الملف {doc_name}\n\n" + text)
        await call.message.answer(text=text)
        await call.answer()

@utils_router.callback_query(MenuAction.filter(F.action== "send_file"))
async def file_sending(call:CallbackQuery,callback_data:MenuAction):
    parent_id=callback_data.parent_id
    ids=database.get_files_ids(parent_id)
    
    if ids == None or ids == []:
        await call.message.answer(text="لا يوجد اي ملفات في هذه القائمة ")
    else:
        for file_id,doc_id,doc_name in ids:
            await call.message.answer_document(document=doc_id,caption=f"ملف رقم : {file_id} ")

@utils_router.callback_query(MenuAction.filter(F.action =="add"))
async def add_button(call:CallbackQuery,callback_data: MenuAction,state:FSMContext,):

    await call.message.answer(text="enter the name of the button")
    await state.update_data(par_id=callback_data.parent_id)
    await state.set_state(create_button.get_name)

@utils_router.callback_query(MenuAction.filter(F.action=="upload"))
async def upload_hundle(call:CallbackQuery,state:FSMContext,callback_data:MenuAction):

    await state.update_data(parent_id=callback_data.parent_id)

    await call.message.answer(text="Please send the files")
    await state.set_state(upload_file.get_file_id)

@utils_router.message(upload_file.get_file_id,F.document)
async def getting_files(msg:Message,state:FSMContext):

    data= await state.get_data()
    parent_id=data.get("parent_id")

    doc_name=msg.document.file_name
    doc_id=msg.document.file_id
    
    builder=ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="✅ Done"))

    await msg.answer(text="watting for your file",reply_markup=builder.as_markup())
    #insert the files into the database
    database.upload_file(parent_id,doc_id,doc_name)
    
    await msg.answer(text=f"file {doc_name} have been uploaded ✅ ")

@utils_router.message(F.text=="✅ Done")
async def handle_stop_upload(msg:Message,state:FSMContext):
    data= await state.get_data()
    parent_id= data.get("parent_id")
    user_id=msg.from_user.id

    await state.clear()
    await msg.answer(text=f"uploading opeartion is finished reloading main menu 🔄️",reply_markup=ReplyKeyboardRemove())

    reply_markup=build_dynamic_menu(parent_id,user_id)
    await msg.answer(text=f"folder: {parent_id}",reply_markup=reply_markup)

@utils_router.callback_query(MenuAction.filter(F.action =="delete"))
async def delete_button_handler(call:CallbackQuery,callback_data:MenuAction):
    parent_id=callback_data.parent_id
    grandparent_id=database.get_parent_of(parent_id)

    database.delete_button_by_id(parent_id)

    new_markup = build_dynamic_menu(str(grandparent_id), call.from_user.id)
    
    await call.message.edit_text("Folder deleted. Returning to parent menu:", reply_markup=new_markup)
    await call.answer("Deleted successfully!")

@utils_router.message(create_button.get_name)
async def createButtonhandle(msg:Message,state:FSMContext):
    name=msg.text

    data= await state.get_data()
    parent_id= data.get("par_id")
    await state.clear()

    database.create_inline_button(name,parent_id)
    new_keyboard = build_dynamic_menu(parent_id,msg.from_user.id)

    await msg.answer(text=f"✅ Added {name} successfully here is the new menu:",reply_markup=new_keyboard)
    

@utils_router.callback_query(MenuAction.filter(F.action == "open"))
async def navigate_menu(call: CallbackQuery, callback_data: MenuAction):
    try:
        print(f"DEBUG: Attempting to build menu for: {callback_data.parent_id}")
        
        markup = build_dynamic_menu(parent_id=callback_data.parent_id,user_id=call.from_user.id)
                                                                                                                                                                                                                                                                                                                                               
        await call.message.edit_text(
            text=f" folder : {callback_data.parent_id} ", 
            reply_markup=markup
        )
        await call.answer()
        
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        await call.answer("Error building menu.")

@utils_router.message(F.text=="help")
async def menu1_hundel(msg:Message):
    await msg.reply(text="use this instruction")
    
@utils_router.callback_query()
async def unknown_callback(call: CallbackQuery):
    print(f"DEBUG: Unhandled callback data: {call.data}")
    await call.answer("This button does nothing yet!")

def build_dynamic_menu(parent_id :str, user_id:str):

    builder = InlineKeyboardBuilder()
    #fetch children
    children = database.get_buttons_by_parent(parent_id)
    
    #add children FIRST
    for child_id, name in children:
        builder.button(
            text=f"📁 {name}", 
            callback_data=MenuAction(action="open", parent_id=str(child_id)).pack()
        )
    
    
    controls = []
    is_root = parent_id is None or str(parent_id).upper() in ["NONE", "NULL","None"]
    admin_list=database.get_admin_ids()
    # create controls as a separate list
    #all users
    if not is_root:
        grandparent = database.get_parent_of(parent_id)
        controls.append(InlineKeyboardButton(text="🔙 رجوع", callback_data=MenuAction(action="open", parent_id=str(grandparent)).pack()))
        controls.append(InlineKeyboardButton(text="🗃️📲 ارسال الملفات المرفوعة", callback_data=MenuAction(action="send_file", parent_id=parent_id).pack()))
        controls.append(InlineKeyboardButton(text="🗃️📲 ارسال قائمة الملفات ", callback_data=MenuAction(action="send_flist", parent_id=parent_id).pack()))
    #admins
    if str(user_id) in admin_list or user_id == config.OWNER_ID:

        controls.append(InlineKeyboardButton(text="🤵📂 send admin list ", callback_data=MenuAction(action="send_admin_list", parent_id=parent_id).pack()))
        controls.append(InlineKeyboardButton(text="➕ Add", callback_data=MenuAction(action="add", parent_id=parent_id).pack()))

        if not is_root:
            controls.append(InlineKeyboardButton(text="🗑️ Del Folder", callback_data=MenuAction(action="delete", parent_id=parent_id).pack()))
            controls.append(InlineKeyboardButton(text="⬆️ Upload", callback_data=MenuAction(action="upload", parent_id=parent_id).pack()))
            controls.append(InlineKeyboardButton(text="🗑️📂 Del file", callback_data=MenuAction(action="delete_f", parent_id=parent_id).pack()))
            
    if is_root and user_id == config.OWNER_ID:
        controls.append(InlineKeyboardButton(text="🤵 Add admin", callback_data=MenuAction(action="add_admin", parent_id=parent_id).pack()))
        controls.append(InlineKeyboardButton(text="👥💬 select support_group", callback_data=MenuAction(action="select_supp_group", parent_id=parent_id).pack()))
        controls.append(InlineKeyboardButton(text="🤵❌ remove admin", callback_data=MenuAction(action="remove_admin_list", parent_id=parent_id).pack()))
    #use builder.row to add the controls as thelast row 
    builder.row(*controls )
    builder.adjust(2, 3)
    return builder.as_markup()
