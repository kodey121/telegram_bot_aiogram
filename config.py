import json
import os 

owner_id=os.getenv('OWNER_ID')
OWNER_ID=owner_id

def create_json():
    settings={
        "supprot_group":None
        
    }
    with open("settings.json","w",encoding="utf-8") as f:
        json.dump(settings,f,indent=4)

def load_settings():
    file_name="settings.json"

    if not(os.path.exists(file_name)):
        return {}
    
    with open("settings.json","r",encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}
    
def write_settings(key,value):
    data=load_settings()
    data[key]=value

    with open("settings.json","w",encoding="utf-8") as f:
        json.dump(data,f,indent=4)
