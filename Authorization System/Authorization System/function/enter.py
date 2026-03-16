####################### БЛОК ДЛЯ ВХОДУ В СИСТЕМУ ####################

import bcrypt
import math
import time
from dataBase import (
    FIELD_LABELS,
    PROFILE_HIDDEN_FIELDS,
    get_auth_users,
    get_regular_users,
    is_admin_username,
)

MAX_FAILED_ATTEMPTS = 3
LOCKOUT_SECONDS = 10

_failed_attempts = 0
_locked_until = 0.0

def check_login(entered_username, entered_password):
    password_bytes = entered_password.encode('utf-8')
    for user in get_auth_users():
        if user["username"] == entered_username:
            saved_hash_bytes = user["password_hash"].encode('utf-8')
            if bcrypt.checkpw(password_bytes, saved_hash_bytes):
                return user 
            else:
                return False            
    return False 


def _is_locked():
    return time.time() < _locked_until


def get_lock_seconds_left():
    if not _is_locked():
        return 0
    return max(0, math.ceil(_locked_until - time.time()))


def reset_lock_state():
    global _failed_attempts, _locked_until
    _failed_attempts = 0
    _locked_until = 0.0


def process_login_attempt(username, password):
    global _failed_attempts, _locked_until

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

    if not username or not password:
        return {
            "ok": False,
            "locked": False,
            "message": "Введіть логін і пароль.",
            "retry_ms": 0,
            "user": None,
            "is_admin": False,
        }

    user = check_login(username.strip(), password)
    if user:
        reset_lock_state()
        return {
            "ok": True,
            "locked": False,
            "message": "",
            "retry_ms": 0,
            "user": user,
            "is_admin": is_admin_username(user.get("username", "")),
        }

    _failed_attempts += 1
    attempts_left = MAX_FAILED_ATTEMPTS - _failed_attempts

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
        "message": f"Неправильний логін або пароль. Залишилось спроб: {attempts_left}",
        "retry_ms": 0,
        "user": None,
        "is_admin": False,
    }


def build_user_profile_rows(user):
    rows = []
    for field, value in user.items():
        if field in PROFILE_HIDDEN_FIELDS:
            continue
        rows.append((FIELD_LABELS.get(field, field), str(value)))
    return rows


def build_admin_cards_data():
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


def get_user_header_name(user):
    header_name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
    if header_name:
        return header_name
    return user.get("username", "Користувач")


def create_session_state():
    return {"user": None, "is_admin": False}


def apply_login_result_to_session(session_state, login_result):
    if login_result.get("ok"):
        session_state["user"] = login_result.get("user")
        session_state["is_admin"] = login_result.get("is_admin", False)


def get_next_window_kind(session_state):
    if not session_state.get("user"):
        return "none"
    return "admin" if session_state.get("is_admin") else "profile"


def get_authenticated_user(session_state):
    return session_state.get("user")







####################### БЛОК ДЛЯ ДОДАТКОВОГО МЕНЮ ####################

def get_family_status(user_dict):
    return f"Ваш сімейний статус: {user_dict['family_status']}"

def get_penalty_status(user_dict):
    status = user_dict["penalty_status"]
    if status == "відсутні":
        return "Штрафи відсутні."
    else:
        return f"Маєте штраф у розмірі: {status}"
    
