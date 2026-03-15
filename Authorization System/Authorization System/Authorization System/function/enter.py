####################### БЛОК ДЛЯ ВХОДУ В СИСТЕМУ ####################

import bcrypt
from function.dataBase import users_list

def check_login(entered_username, entered_password):
    password_bytes = entered_password.encode('utf-8')
    for user in users_list:
        if user["username"] == entered_username:
            saved_hash_bytes = user["password_hash"].encode('utf-8')
            if bcrypt.checkpw(password_bytes, saved_hash_bytes):
                return user 
            else:
                return False            
    return False 

def register_user(username, password):
    pass # TODO: Implement this function



####################### БЛОК ДЛЯ ДОДАТКОВОГО МЕНЮ ####################

def get_family_status(user_dict):
    return f"Ваш сімейний статус: {user_dict['family_status']}"

def get_penalty_status(user_dict):
    status = user_dict["penalty_status"]
    if status == "відсутні":
        return "Штрафи відсутні."
    else:
        return f"Маєте штраф у розмірі: {status}"
    
