import importlib
import os


ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), ".."))
KEYS_DIR = os.path.join(ROOT_DIR, "keys")


class Config:
    HOST = os.getenv("SW_HOST", "127.0.0.1")
    PORT = int(os.getenv("SW_PORT", 10022))
    BANNER = os.getenv("SW_BANNER", "SSH-2.0-OpenSSH_7.4").replace("SSH-2.0-", "")
    DATABASE_URI = os.getenv("SW_DATABASE_URI", "./brain.db")
    SERVER_FACTORY = os.getenv("SW_SERVER_FACTORY", "SwitcherooServer")
    LOGFILE = os.getenv("SW_LOGFILE", None)
    CREDENTIALS = os.getenv("SW_CREDENTIALS", None)
    HOST_KEYS = [
        os.path.join(KEYS_DIR, "ssh_host_dsa_key"),
        os.path.join(KEYS_DIR, "ssh_host_rsa_key"),
    ]
    _credentials = None

    @classmethod
    def get_server_factory(cls):
        server_module = importlib.import_module("switcheroo.server")
        server_factory = getattr(server_module, cls.SERVER_FACTORY)
        return server_factory

    @classmethod
    def load_credentials(cls):
        if cls._credentials is not None:
            return cls._credentials
        if isinstance(cls.CREDENTIALS, (list, tuple, set)):
            cls._credentials = list(cls.CREDENTIALS)
            return cls._credentials
        if isinstance(cls.CREDENTIALS, str):
            with open(cls.CREDENTIALS) as fin:
                creds = []
                for line in fin:
                    username, password = line.split(":", 1)
                    creds.append((username, password[:-1]))
                cls._credentials = creds
                return cls._credentials

    @classmethod
    def reload_credentials(cls, *args):
        cls._credentials = None
        cls.load_credentials()
