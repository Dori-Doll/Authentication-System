import bcrypt
import sys
import io

#УВАЖНООО!!! Цей шматок треба щоб UTF-8 відображав українські літери, адже кодування cp1252 їх не підтримує. Без нього НІЧОГО НЕ БУДЕ ПРАЦЮВАТИ!!!!!!
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

enter = {
    "alex_h": "10101210",
    "soNYA": "12345678",
    "Vasyl98": "87654321",
    "MAXIMUS": "14785236",
    "DmytrOK": "D123321D",
    "Rosti": "951Rosti",
    "Vladdd": "7896525T",
    "Yarou": "1254ya36",
    "Olena_P": "200Olena",
    "Svit0101": "10101010"
}

for login, password in enter.items():
    password_bytes = password.encode('utf-8')

    salt = bcrypt.gensalt()

    hashed_bytes = bcrypt.hashpw(password_bytes, salt)


    hashed_text = hashed_bytes.decode('utf-8')
    
    print(f"Логін: {login}")
    print(f"{hashed_text}")
    print("-" * 65)
  
