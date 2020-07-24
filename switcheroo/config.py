import importlib
import os


class Config:
    HOST = os.getenv("SW_HOST", "127.0.0.1")
    PORT = int(os.getenv("SW_PORT", 10022))
    BANNER = os.getenv("SW_BANNER", "SSH-2.0-OpenSSH_7.4")
    DATABASE_URI = os.getenv("SW_DATABASE_URI", "./brain.db")
    SERVER_CLASS = os.getenv("SW_AUTH_HANDLER", "SwitcherooSSHServer")
    HOST_KEYS = ["/home/me/Documents/code/switcheroo/keys/ssh_host_dsa_key", "/home/me/Documents/code/switcheroo/keys/ssh_host_rsa_key"]

    @classmethod
    def get_server_class(cls):
        server_module = importlib.import_module("switcheroo.server")
        server_class = getattr(server_module, cls.SERVER_CLASS)
        return server_class