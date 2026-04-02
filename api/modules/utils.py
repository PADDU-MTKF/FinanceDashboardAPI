import secrets
import string

from django.core.cache import cache


def generateToken(length=20):
    characters = string.ascii_letters + string.digits  # A-Z, a-z, 0-9
    return ''.join(secrets.choice(characters) for _ in range(length))


    