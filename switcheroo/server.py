import asyncio
import logging

import asyncssh

from switcheroo import utils

logger = logging.getLogger("switcheroo")


class BaseSSHServer(asyncssh.SSHServer):

    def connection_made(self, con):
        self.con = con
        self.host, self.port = con.get_extra_info("peername")

    def begin_auth(self, username):
        return True

    def public_key_auth_supported(self):
        return True

    def password_auth_supported(self):
        return True

    def validate_password(self, username, password):
        return False

    def validate_public_key(self, username, key):
        return False


class LoggingSSHServer(BaseSSHServer):

    def validate_password(self, username, password):
        logger.info("auth='password' host=%r username=%r password=%r", f"{self.host}:{self.port}", username, password)
        return False

    def validate_public_key(self, username, key):
        sha_fingerprint = key.get_fingerprint(hash_name="sha256")[7:]
        md5_fingerprint = key.get_fingerprint(hash_name="md5")[4:]
        logger.info("auth='pubkey' host=%r md5=%r sha=%r", f"{self.host}:{self.port}", md5_fingerprint, sha_fingerprint)
        return False


class SwitcherooSSHServer(LoggingSSHServer):

    async def switcheroo(self, username, password):
        """
        Use the attacker's credentials against himself.

        :param username:
        :param password:
        :return:
        """
        try:
            async with asyncssh.connect(self.host, username=username, password=password, known_hosts=None):
                logger.info("auth='password' host=%r username=%r password=%r valid=true", f"{self.host}:{self.port}", username, password)
                return False
        except Exception:
            logger.info("auth='password' host=%r username=%r password=%r valid=false", f"{self.host}:{self.port}", username, password)
        return False

    def validate_password(self, username, password):
        return asyncio.wait_for(self.switcheroo(username, password), timeout=4.0)
