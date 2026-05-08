from uuid6 import uuid7


def generate_id() -> str:
    return uuid7().hex[:12]