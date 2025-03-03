import hashlib
import uuid
from typing import Optional


class ApiKey:
    def __init__(self, raw_key: Optional[str] = None):
        if raw_key is None:
            raw_key = self.generate_api_key()
        self.raw_key = raw_key
        self.key_hash = self.hash_api_key(self.raw_key)

    @staticmethod
    def generate_api_key():
        return uuid.uuid4().hex

    @staticmethod
    def hash_api_key(raw_key: str):
        return hashlib.sha256(raw_key.encode()).hexdigest()
