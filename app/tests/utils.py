import random
import string
from datetime import date, time, timedelta

from app.core.config import settings

CORRECT_LOGIN_DATA = {
    "username": settings.FIRST_ADMIN_EMAIL,
    "password": settings.FIRST_ADMIN_PASSWORD,
}

INCORRECT_LOGIN_DATA = {
    "username": settings.FIRST_ADMIN_EMAIL,
    "password": settings.FIRST_ADMIN_PASSWORD + "incorret",
}


def random_lower_string() -> str:
    return "".join(random.choices(string.ascii_lowercase, k=32))


def random_email() -> str:
    return f"{random_lower_string()}@{random_lower_string()}.com"


def random_date():
    start = date.today()
    offset = random.randint(0, 365)
    return start - timedelta(days=offset)


def random_time():
    hour = random.randint(0, 23)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    return time(hour=hour, minute=minute, second=second)
