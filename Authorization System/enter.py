####################### БЛОК ДЛЯ ВХОДУ В СИСТЕМУ ####################

from dataBase import user_list
def check_login(entered_username, entered_password):
    for user in user_list:
        if user["username"] == entered_username:
            if user["password_hash"] == entered_password:
                return user                 
    return False

####################### БЛОК ДЛЯ ДОДАТКОВОГО МЕНЮ ####################

def get_family_status(user_dict):
    return f"Ваш сімейний статус: {user_dict['family_status']}"

def get_penalty_status(user_dict):
    status = user_dict["penalty_status"]
    if status == "відсутні":
        return "Штрафи відсутні."
    else:
        return f"Маєте штраф у розмірі: {status}"
