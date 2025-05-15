import pytest
import bcrypt

from src.adapters.password_hasher import BcryptPasswordHasher
from src.adapters.password_hasher import BcryptNamesHasher

def test_hash_password():
    password_hasher = BcryptPasswordHasher(salt_rounds=12)
    password = "myPassword"
    hashed_password = password_hasher.hash_password(password)
    assert password != hashed_password

    hashed_password2 = password_hasher.hash_password(password)
    assert hashed_password != hashed_password2

def test_verify_password():
    password_hasher = BcryptPasswordHasher(salt_rounds=12)
    password = "myPassword"
    hashed_password = password_hasher.hash_password(password)
    assert password_hasher.verify_password(password, hashed_password) is True
    assert password_hasher.verify_password("wrong", hashed_password) is False


def test_hash_names():
    names_hasher = BcryptNamesHasher(salt_rounds=12)
    name = "myName"
    hashed_name = names_hasher.hash_name(name)
    assert name != hashed_name

    hashed_name2 = names_hasher.hash_name(name)
    assert hashed_name != hashed_name2
