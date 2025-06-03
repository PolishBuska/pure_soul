import base64

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
        bcrypt_hash = bcrypt.hashpw(name.encode(), salt)

        # 2) Drop the leading `$2b$…$` metadata and keep only the 31‑byte digest
        digest = bcrypt_hash.split(b"$")[-1]

        urlsafe = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
        return urlsafe