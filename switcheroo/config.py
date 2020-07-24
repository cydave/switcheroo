import importlib
import os


class Config:
    DATABASE_URI = os.getenv("DATABASE_URI", "./brain.db")
    AUTH_HANDLER = os.getenv("AUTH_HANDLER", "SwitcherooAuth")

    @classmethod
    def get_auth_handler(cls):
        auth_module = importlib.import_module('switcheroo.auth')
        auth_handler = getattr(auth_module, cls.AUTH_HANDLER)
        return auth_handler
