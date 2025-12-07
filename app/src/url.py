import random
import string
from dataclasses import dataclass


@dataclass
class UrlLength:
    MAX_LENGTH: int = 7
    MIN_LENGTH: int = 7

    @classmethod
    def get(cls) -> int:
        return random.randint(cls.MIN_LENGTH, cls.MAX_LENGTH)

def create_url() -> str: # Url
    return "".join(random.choices(string.ascii_letters, k=UrlLength.get()))
