import sqlite3
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import KeyboardButton

def get_connection():
    conn = sqlite3.connect("my_dpython --veata.db")
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn=get_connection()
    cur=conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS button_data(id INTEGER PRIMARY KEY AUTOINCREMENT, 
            title TEXT, file_id TEXT, parent TEXT ,FOREIGN KEY (parent) REFERENCES button_data(id) ON DELETE CASCADE) """)
    conn.commit()
    conn.close()

def table2():
      
      conn=get_connection()
      cur=conn.cursor()
      cur.execute("""CREATE TABLE IF NOT EXISTS file_data(id INTEGER PRIMARY KEY AUTOINCREMENT,file_id TEXT, button_id INTEGER 

                                  ,file_name TEXT,FOREIGN KEY (button_id) REFERENCES button_data(id) ON DELETE CASCADE )""")
      conn.close()

def table3():
      conn=get_connection()
      cur=conn.cursor()
      cur.execute("CREATE TABLE IF NOT EXISTS admin_data(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id TEXT,user_name TEXT) ")
      conn.close()
      
init_db()
table2()
table3()

def upload_file(parent_id,file_id:str,doc_name):
        conn=get_connection()
        cur=conn.cursor()
        cur.execute("INSERT INTO file_data (file_id,button_id,file_name) VALUES (?,?,?) ",(file_id,parent_id,doc_name))
        conn.commit()
        conn.close()

def get_file_name_of(id:str):
        conn=get_connection()
        cur=conn.cursor()
        cur.execute("SELECT title FROM button_data WHERE parent = ? ",(id,))
        result=cur.fetchone()
        conn.close()
        return result

def get_buttons_by_parent(parent_id):
    conn = get_connection()
    cur = conn.cursor()
    is_root = parent_id is None or str(parent_id).upper() in ["NONE", "NULL"]

    if is_root:
       
       cur.execute("SELECT id, title FROM button_data WHERE parent IS NULL")
    else:
        try:
                cur.execute("SELECT id, title FROM button_data WHERE parent = ?", (int(parent_id),))
        except ValueError:
              cur.execute("SELECT id, title FROM button_data WHERE parent IS NULL")

    children = cur.fetchall()
    print(f"DEBUG DB: Found {len(children)} items for parent {parent_id}") #Debug
    conn.close()
    return children


def get_parent_of(current_menu_id):    
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT parent FROM button_data WHERE id = ?", (current_menu_id,))
    result = cur.fetchone()
    conn.close()
    
    if result and result[0] is not None:
        return str(result[0])
    
    return None # Return the string NULL if we hit the top

def create_inline_button(name,parent_id):
        conn=get_connection()
        cur=conn.cursor()
        is_root = parent_id is None or str(parent_id).upper() in ["NONE", "NULL"]
        if is_root: 
              parent_id=None
        else:
              parent_id=int(parent_id)

        cur.execute("INSERT INTO button_data (title, parent) VALUES (?, ?)",(name,parent_id))
        conn.commit()
        conn.close()
        
def get_files_ids(parent_id):
        conn=get_connection()
        cur=conn.cursor()
        cur.execute("SELECT id,file_id,file_name FROM file_data  WHERE button_id = ? ",(parent_id,))
        results=cur.fetchall()
        conn.close()
        return results

def delete_button_by_id(parent_id):
        conn=get_connection()
        cur=conn.cursor()
        cur.execute("DELETE FROM button_data WHERE id=?",[parent_id])
        conn.commit()
        conn.close()

def remove_uploaded_file(parent_id):
        conn=get_connection()
        cur=conn.cursor()
        cur.execute("DELETE FROM file_data WHERE button_id= ? ",[parent_id])
        conn.commit()
        conn.close()
        
#admins section 
def add_admin(user_id,user_name):
        conn=get_connection()
        cur=conn.cursor()
        cur.execute("INSERT INTO admin_data (user_id,user_name) VALUES (?,?) ",(user_id,user_name))
        conn.commit()
        conn.close()

def remove_admin(user_id):
        conn=get_connection()
        cur=conn.cursor()
        cur.execute("DELETE FROM admin_data WHERE user_id = ?",(user_id,))
        conn.commit()
        conn.close()

def get_admin_ids():
        conn=get_connection()
        cur=conn.cursor()
        cur.execute("SELECT user_id FROM admin_data")
        admins = [str(row[0]) for row in cur.fetchall()]
        conn.close()
        return admins

def get_admin_info():
        conn=get_connection()
        cur=conn.cursor()
        cur.execute("SELECT user_id,user_name FROM admin_data")
        admins =cur.fetchall()
        conn.close()
        return admins
