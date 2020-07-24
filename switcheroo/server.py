import logging

import asyncssh

from switcheroo.config import Config


logger = logging.getLogger("switcheroo")


class SSHServer(asyncssh.SSHServer):

    def connection_made(self, con):
        self.con = con
        self.peer = con.get_extra_info("peername")
        self._auth_handler = Config.get_auth_handler()

    def begin_auth(self, username):
        return True

    def public_key_auth_supported(self):
        return True

    def password_auth_supported(self):
        return True

    def validate_password(self, username, password):
        return self._auth_handler.validate_password(peer=self.peer, username=username, password=password)

    def validate_public_key(self, username, key):
        return self._auth_handler.validate_public_key(peer=self.peer, pubkey=key)
