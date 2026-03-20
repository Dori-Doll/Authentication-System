# Важливо розуміти перед початком, що структура програми виглядає наступним чином:
#   enter.py – це функціонал. Він відповідає наприклад за перевірку логіна/пароля (def check_login(entered_username, entered_password)). Рахування невдалих спроб (_failed_attempts = 0), дається 3 спроби (MAX_FAILED_ATTEMPTS = 3), далі йде 10-секундне блокування (LOCKOUT_SECONDS = 10). Підготовку повідомлень для графічного інтерфейсу (process_login_attempt). Підготовку даних профілю для звичайного вікна користувача (build_user_profile_rows).Підготовку даних для вікна адміністратора (build_admin_cards_data).
#   dataBase.py – це сховище де зберігаються користувачі та їх дані.
#   gui.py – це інтерфейс, тобто вікна, кнопки, текстові поля і.т.д. Назва умовна





####################### БЛОК ДЛЯ ВХОДУ В СИСТЕМУ ####################



import bcrypt
import math
import time
import json
import re
import calendar
from datetime import date, datetime
from pathlib import Path
# Імпортується файл dataBase.py де записана інформація про користувачів.
from .dataBase import (
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


####################### БЛОК ДЛЯ РЕЄСТРАЦІЇ ####################

# Шляхи до файлів, які потрібні для реєстрації.
_BASE_DIR = Path(__file__).resolve().parent
_DATABASE_FILE_PATH = _BASE_DIR / "dataBase.py"
_LOCALITIES_FILE_PATH = _BASE_DIR.parent / "ukrainian_regions_and_localities.json"

# Варіанти для випадаючих списків у вікні реєстрації.
SEX_OPTIONS_DISPLAY = ["Чоловіча", "Жіноча"]
SEX_CODE_MAP = {"Чоловіча": "Ч", "Жіноча": "Ж"}
FAMILY_STATUS_OPTIONS_BY_SEX = {
    "Чоловіча": ["не одружений", "одружений"],
    "Жіноча": ["не одружена", "одружена"],
}

MIN_BIRTH_YEAR = 1900

_localities_cache = None
_localities_set_cache = None


def _load_localities_cache():
    # Завантажуємо список населених пунктів із JSON лише один раз.
    global _localities_cache, _localities_set_cache
    if _localities_cache is not None and _localities_set_cache is not None:
        return

    with _LOCALITIES_FILE_PATH.open("r", encoding="utf-8") as json_file:
        regions_data = json.load(json_file)

    localities = []
    for region_localities in regions_data.values():
        for locality in region_localities:
            if isinstance(locality, str):
                locality_name = locality.strip()
                if locality_name:
                    localities.append(locality_name)

    # Прибираємо дублікати, але зберігаємо початковий порядок.
    unique_localities = list(dict.fromkeys(localities))
    _localities_cache = unique_localities
    _localities_set_cache = set(unique_localities)


def get_sex_options_display():
    # Повертає варіанти для поля "Стать".
    return list(SEX_OPTIONS_DISPLAY)


def get_family_status_options_display(sex_display):
    # Повертає правильні варіанти сімейного стану залежно від обраної статі.
    return list(FAMILY_STATUS_OPTIONS_BY_SEX.get(sex_display, []))


def get_locality_suggestions(query, limit=20):
    # Повертає підказки населених пунктів за введеним початком назви.
    _load_localities_cache()
    search_text = (query or "").strip().casefold()
    if not search_text:
        return []

    suggestions = []
    for locality in _localities_cache:
        if locality.casefold().startswith(search_text):
            suggestions.append(locality)
            if len(suggestions) >= limit:
                break
    return suggestions


def get_birth_year_options():
    # Повертає роки для списку від поточного року до 1900.
    current_year = date.today().year
    return [str(year) for year in range(current_year, MIN_BIRTH_YEAR - 1, -1)]


def get_birth_month_options():
    # Повертає варіанти місяців у форматі 01..12.
    return [f"{month:02d}" for month in range(1, 13)]


def get_birth_day_options(year_value, month_value):
    # Повертає правильну кількість днів для обраного місяця і року.
    try:
        year = int(year_value)
        month = int(month_value)
        days_in_month = calendar.monthrange(year, month)[1]
    except Exception:
        days_in_month = 31
    return [f"{day:02d}" for day in range(1, days_in_month + 1)]


def get_modal_birth_year_options():
    # Повертає роки для покрокового вибору дати народження у вікні.
    return get_birth_year_options()


def get_modal_birth_month_options(selected_year):
    # Для поточного року дозволеноо лише місяці до поточного включно.
    try:
        year_number = int(selected_year)
    except (TypeError, ValueError):
        return []

    today = date.today()
    max_month = today.month if year_number == today.year else 12
    return [f"{month:02d}" for month in range(1, max_month + 1)]


def get_modal_birth_day_options(selected_year, selected_month):
    # Повертає дні з урахуванням місяця/року та обмеженням на майбутні дати.
    month_options = get_modal_birth_month_options(selected_year)
    month_text = f"{int(selected_month):02d}" if str(selected_month).isdigit() else ""
    if month_text not in month_options:
        return []

    day_options = get_birth_day_options(selected_year, selected_month)

    try:
        year_number = int(selected_year)
        month_number = int(selected_month)
    except (TypeError, ValueError):
        return []

    today = date.today()
    if year_number == today.year and month_number == today.month:
        return [f"{day:02d}" for day in range(1, today.day + 1)]

    return day_options


def build_modal_birth_selection(day_value, month_value, year_value):
    # Формує дані обраної дати для gui.py після покрокового вибору.
    birth_date_text, birth_date_error = build_birth_date(day_value, month_value, year_value)
    if birth_date_error:
        return None

    return {
        "day": f"{int(day_value):02d}",
        "month": f"{int(month_value):02d}",
        "year": str(int(year_value)),
        "display": birth_date_text,
    }


def build_birth_date(day_value, month_value, year_value):
    # Збирає і перевіряє дату народження у форматі ДД.ММ.РРРР.
    if not day_value or not month_value or not year_value:
        return None, "Оберіть повну дату народження."

    if not str(day_value).isdigit() or not str(month_value).isdigit() or not str(year_value).isdigit():
        return None, "Оберіть повну дату народження."

    try:
        day_number = int(day_value)
        month_number = int(month_value)
        year_number = int(year_value)
        birthday = date(year_number, month_number, day_number)
    except ValueError:
        return None, "Неправильна дата народження."

    today = date.today()
    if birthday < date(MIN_BIRTH_YEAR, 1, 1) or birthday > today:
        return None, "Дата народження має бути у межах 1900 року і до сьогодні."

    return birthday.strftime("%d.%m.%Y"), ""


def _is_valid_locality(locality_name):
    # Дозволяємо тільки ті населені пункти, які реально є у файлі JSON.
    _load_localities_cache()
    return locality_name in _localities_set_cache


def _normalize_penalty_status(raw_value):
    # Якщо поле штрафів порожнє, автоматично ставимо "відсутні".
    value = (raw_value or "").strip()
    return value if value else "відсутні"


def _is_username_available(username):
    # Перевіряємо, що логін ще не зайнятий.
    clean_username = username.strip()
    for user in get_auth_users():
        if user.get("username") == clean_username:
            return False
    return True


def _build_password_hash(password):
    # Перетворюємо пароль у bcrypt-хеш перед записом у базу.
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt).decode("utf-8")


def _extract_next_user_number(database_text):
    # Знаходимо наступний номер користувача: після user_10 буде user_11 і т.д.
    numbers = [int(n) for n in re.findall(r"\buser_(\d+)\s*=", database_text)]
    return max(numbers) + 1 if numbers else 1


def _build_user_block(variable_name, user_data):
    # Формуємо текст нового блоку user_N = {...} у стандартному порядку полів.
    ordered_fields = [
        "username",
        "password_hash",
        "first_name",
        "last_name",
        "father_name",
        "birth_place",
        "birth_date",
        "sex",
        "family_status",
        "penalty_status",
    ]

    lines = [f"{variable_name} = {{"]
    for field in ordered_fields:
        value = str(user_data.get(field, ""))
        lines.append(f'    "{field}": "{value}",')
    lines.append("}")
    lines.append("")
    return "\n".join(lines)


def _append_user_to_database_file(user_data):
    # Додаємо нового користувача у dataBase.py і оновлюємо user_list.
    database_text = _DATABASE_FILE_PATH.read_text(encoding="utf-8")

    next_number = _extract_next_user_number(database_text)
    variable_name = f"user_{next_number}"
    new_block = _build_user_block(variable_name, user_data)

    admin_match = re.search(r"\nadmin\s*=\s*\{", database_text)
    if not admin_match:
        raise ValueError("Не знайдено блок admin у dataBase.py")

    insert_at = admin_match.start()
    updated_text = database_text[:insert_at] + "\n" + new_block + database_text[insert_at:]

    user_list_pattern = r"user_list\s*=\s*\[(.*?)\]"
    user_list_match = re.search(user_list_pattern, updated_text, flags=re.DOTALL)
    if not user_list_match:
        raise ValueError("Не знайдено user_list у dataBase.py")

    current_items = [item.strip() for item in user_list_match.group(1).split(",") if item.strip()]
    if variable_name not in current_items:
        current_items.append(variable_name)

    replacement = f"user_list = [{', '.join(current_items)}]"
    updated_text = re.sub(user_list_pattern, replacement, updated_text, count=1, flags=re.DOTALL)

    _DATABASE_FILE_PATH.write_text(updated_text, encoding="utf-8")
    return variable_name


def _add_user_to_runtime_collections(new_user_data):
    # Додаємо нового користувача у поточні списки в пам'яті,
    # щоб вхід працював без перезапуску програми.
    regular_users = get_regular_users()
    auth_users = get_auth_users()

    regular_users.append(new_user_data)

    if auth_users and is_admin_username(auth_users[-1].get("username", "")):
        auth_users.insert(len(auth_users) - 1, new_user_data)
    else:
        auth_users.append(new_user_data)

def register_new_user(registration_data):
    # Головна функція реєстрації для gui.py.
    # Приймає введені дані, перевіряє їх і додає користувача у базу.
    username = (registration_data.get("username") or "").strip()
    password = registration_data.get("password") or ""
    first_name = (registration_data.get("first_name") or "").strip()
    last_name = (registration_data.get("last_name") or "").strip()
    father_name = (registration_data.get("father_name") or "").strip()
    birth_place = (registration_data.get("birth_place") or "").strip()
    sex_display = (registration_data.get("sex_display") or "").strip()
    family_status_display = (registration_data.get("family_status_display") or "").strip()
    penalty_status = _normalize_penalty_status(registration_data.get("penalty_status") or "")
    birth_day = (registration_data.get("birth_day") or "").strip()
    birth_month = (registration_data.get("birth_month") or "").strip()
    birth_year = (registration_data.get("birth_year") or "").strip()
    birth_place_selected = bool(registration_data.get("birth_place_selected"))

    if not username:
        return {"ok": False, "message": "Введіть логін."}
    if len(username) < 4:
        return {"ok": False, "message": "Логін має містити щонайменше 4 символи."}
    if username.isdigit():
        return {"ok": False, "message": "Логін не може складатися лише з цифр."}
    if not _is_username_available(username):
        return {"ok": False, "message": "Такий логін вже існує. Оберіть інший."}

    if not password:
        return {"ok": False, "message": "Введіть пароль."}
    if len(password) < 4:
        return {"ok": False, "message": "Пароль має містити щонайменше 4 символи."}

    if not first_name or not last_name or not father_name:
        return {"ok": False, "message": "Заповніть ім'я, прізвище та по батькові."}

    birth_date_text, birth_date_error = build_birth_date(birth_day, birth_month, birth_year)
    if birth_date_error:
        return {"ok": False, "message": birth_date_error}

    if not birth_place:
        return {"ok": False, "message": "Оберіть населений пункт зі списку."}
    if not birth_place_selected:
        return {"ok": False, "message": "Для місця народження потрібно обрати варіант зі списку підказок."}
    if not _is_valid_locality(birth_place):
        return {"ok": False, "message": "Потрібно обрати населений пункт саме зі списку."}

    if sex_display not in SEX_CODE_MAP:
        return {"ok": False, "message": "Оберіть стать зі списку."}

    valid_family_options = get_family_status_options_display(sex_display)
    if family_status_display not in valid_family_options:
        return {"ok": False, "message": "Оберіть сімейний стан зі списку."}

    new_user = {
        "username": username,
        "password_hash": _build_password_hash(password),
        "first_name": first_name.upper(),
        "last_name": last_name.upper(),
        "father_name": father_name.upper(),
        "birth_place": birth_place,
        "birth_date": birth_date_text,
        "sex": SEX_CODE_MAP[sex_display],
        "family_status": family_status_display,
        "penalty_status": penalty_status,
    }

    try:
        created_variable = _append_user_to_database_file(new_user)
        _add_user_to_runtime_collections(new_user)
    except Exception as error:
        return {"ok": False, "message": f"Помилка збереження у dataBase.py: {error}"}

    return {
        "ok": True,
        "message": "Реєстрація успішна.",
        "user": new_user,
    }






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
