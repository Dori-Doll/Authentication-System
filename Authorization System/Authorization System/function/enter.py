# Важливо розуміти перед початком, що структура програми виглядає наступним чином:
#   enter.py – це функціонал. Він відповідає наприклад за перевірку логіна/пароля (def check_login(entered_username, entered_password)). Рахування невдалих спроб (_failed_attempts = 0), дається 3 спроби (MAX_FAILED_ATTEMPTS = 3), далі йде 10-секундне блокування (LOCKOUT_SECONDS = 10). Підготовку повідомлень для графічного інтерфейсу (process_login_attempt). Підготовку даних профілю для звичайного вікна користувача (build_user_profile_rows).Підготовку даних для вікна адміністратора (build_admin_cards_data).
#   dataBase.py – це сховище де зберігаються користувачі та їх дані.
#   gui.py – це інтерфейс, тобто вікна, кнопки, текстові поля і.т.д. Назва умовна






####################### БЛОК ДЛЯ ВХОДУ В СИСТЕМУ ####################



import bcrypt
import math
import time
# Імпортується файл dataBase.py де записана інформація про користувачів.
from dataBase import (
    FIELD_LABELS,
    PROFILE_HIDDEN_FIELDS,
    get_auth_users,
    get_regular_users,
    is_admin_username,
)

# Перший рядок це скільки разів можна помилитися з паролем.
# Дургий це блокування на 10 секунд.
MAX_FAILED_ATTEMPTS = 3
LOCKOUT_SECONDS = 10

# Це службові змінні:
# _failed_attempts - скільки разів підряд ввели неправильні дані.
# _locked_until - до якого моменту часу вхід заблокований.
_failed_attempts = 0
_locked_until = 0.0

def check_login(entered_username, entered_password):
    # Тут перевіряється логін і пароль з базою користувачів.
    # Якщо все правильно, то повертає дані користувача.
    # Якщо ні - повертає False.
    password_bytes = entered_password.encode('utf-8')
    for user in get_auth_users():
        if user["username"] == entered_username:
            saved_hash_bytes = user["password_hash"].encode('utf-8')
            if bcrypt.checkpw(password_bytes, saved_hash_bytes):
                return user 
            else:
                return False            
    return False 

# Перевірка чи зараз вхід заблокований чи ні.
def _is_locked():
    return time.time() < _locked_until

#Скільки секунд залишилося до розблокування.
def get_lock_seconds_left():
    if not _is_locked():
        return 0
    return max(0, math.ceil(_locked_until - time.time()))

# Скидання лічильнику помилок і зняття блокування.
def reset_lock_state():


    global _failed_attempts, _locked_until
    _failed_attempts = 0
    _locked_until = 0.0

# Головна функція входу для gui.py (або іншого файлу де ти пишеш інртерфейс). Вона повертає результат, а gui.py вирішує, що показати на екрані.
# ！！！！！！！！！！！！！！！！！ВАЖЛИВО！！！！！！！！！！！！！！！！！！！
# Далі назва "gui.py" буде використовуватися як файл, що відповідає за інтерфейс (ти можеш назвати його по своєму.)
    
def process_login_attempt(username, password):
    
    global _failed_attempts, _locked_until

    # Якщо вхід тимчасово заблокований - з'являється повідомлення.
    if _is_locked():
        seconds_left = get_lock_seconds_left()
        return {
            "ok": False,
            "locked": True,
            "message": f"3 невдалі спроби. Спробуйте знову через {seconds_left} секунд.",
            "retry_ms": seconds_left * 1000,
            "user": None,
            "is_admin": False,
        }

    # Якщо поля логін або пароль порожні - просимо ввести їх.
    if not username or not password:
        return {
            "ok": False,
            "locked": False,
            "message": "Введіть логін і пароль.", # Повідомлення, що виводиться.
            "retry_ms": 0,
            "user": None,
            "is_admin": False,
        }

    # Перевірка, чи правильні введені дані.
    user = check_login(username.strip(), password)
    if user:
        # Успішний вхід, прибирається блокування.
        reset_lock_state()
        return {
            "ok": True,
            "locked": False,
            "message": "",
            "retry_ms": 0,
            "user": user,
            "is_admin": is_admin_username(user.get("username", "")),
        }

    # Якщо пароль неправильний кількість неправильних спроб накопичується (максимум 3).
    _failed_attempts += 1
    attempts_left = MAX_FAILED_ATTEMPTS - _failed_attempts

    # Якщо спроб більше не залишилось - вхід блокується.
    if attempts_left <= 0:
        _locked_until = time.time() + LOCKOUT_SECONDS
        return {
            "ok": False,
            "locked": True,
            "message": f"3 невдалі спроби. Спробуйте знову через {LOCKOUT_SECONDS} секунд.",
            "retry_ms": LOCKOUT_SECONDS * 1000,
            "user": None,
            "is_admin": False,
        }


    return {
        "ok": False,
        "locked": False,
        "message": f"Неправильний логін або пароль. Залишилось спроб: {attempts_left}", #Повідомлення що з'являється, якщо спроби ще є.
        "retry_ms": 0,
        "user": None,
        "is_admin": False,
    }

    # Готує дані для особистого кабінету користувача в gui.py.
    # Службові поля (наприклад хеш пароля) не показуються користувачеві, вони показуються лише у кабінеті адміністратору.
def build_user_profile_rows(user):

    rows = []
    for field, value in user.items():
        if field in PROFILE_HIDDEN_FIELDS:
            continue
        rows.append((FIELD_LABELS.get(field, field), str(value)))
    return rows


def build_admin_cards_data():
    # Готує список карток для вікна адміністратора в gui.py.
    # Тут тільки звичайні користувачі (без адміна), у тому ж порядку, що в базі.
    cards = []
    for index, user in enumerate(get_regular_users(), start=1):
        rows = [(FIELD_LABELS.get(field, field), str(value)) for field, value in user.items()]
        cards.append(
            {
                "title": f"Користувач {index}: {user.get('username', '')}",
                "rows": rows,
            }
        )
    return cards

# Ця функція вибирає текст для заголовка вікна профілю.
def get_user_header_name(user):
    header_name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
    if header_name:
        return header_name
    return user.get("username", "Користувач")




# Створює початковий стан програми до авторизації. Тобто коли ніхто не увійшов ще.
def create_session_state():
    return {"user": None, "is_admin": False}


def apply_login_result_to_session(session_state, login_result):
    # Після успішного входу записує, хто саме увійшов. Це необхідно, щоб gui.py відкрив правильне наступне вікно.
    if login_result.get("ok"):
        session_state["user"] = login_result.get("user")
        session_state["is_admin"] = login_result.get("is_admin", False)


def get_next_window_kind(session_state):
    # Каже gui.py яке вікно відкривати далі: адміністраторське, профіль користувача або нічого.
    if not session_state.get("user"):
        return "none"
    return "admin" if session_state.get("is_admin") else "profile"


def get_authenticated_user(session_state):
    # Повертає дані користувача, який успішно увійшов.
    return session_state.get("user")







####################### БЛОК ДЛЯ ДОДАТКОВОГО МЕНЮ ###################
 

# Інформація для цього блоку береться напряму із dataBase.py.



def get_family_status(user_dict):
    # Показує готовий текст про сімейний стан.
    return f"Ваш сімейний статус: {user_dict['family_status']}"

def get_penalty_status(user_dict):
    # Показує готовий текст про штрафи. 
    status = user_dict["penalty_status"]
    if status == "відсутні":
        return "Штрафи відсутні."
    else:
        return f"Маєте штраф у розмірі: {status}"
    
