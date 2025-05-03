import bcrypt

from src.application.common.names_hasher import NamesHasher
from src.application.common.password_hasher import PasswordHasher



class BcryptPasswordHasher(PasswordHasher):
    def __init__(self, salt_rounds: int = 12):
        self.salt_rounds = salt_rounds

    def hash_password(self, password: str) -> str:
        """
        Hash the provided password.
        :param password: The plaintext password to hash.
        :return: The hashed password.
        """
        salt = bcrypt.gensalt(rounds=self.salt_rounds)
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed_password.decode('utf-8')

    def verify_password(self, password: str, hashed_password: str) -> bool:
        res = bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
        return res

class BcryptNamesHasher(NamesHasher):
    def __init__(self, salt_rounds: int = 12):
        self.salt_rounds = salt_rounds
    def hash_name(self, name: str) -> str:
        salt = bcrypt.gensalt(rounds=self.salt_rounds)
        hashed_name = bcrypt.hashpw(name.encode('utf-8'), salt)
        return hashed_name.decode('utf-8')
