import asyncio
import logging

import asyncssh
from async_lru import alru_cache

from switcheroo import utils
from switcheroo.config import Config

logger = logging.getLogger("switcheroo")


class BaseServer(asyncssh.SSHServer):
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


class LoggingServer(BaseServer):
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


@alru_cache(maxsize=500)
async def _check_credentials(host, username, password):
    try:
        async with asyncssh.connect(host, username=username, password=password, known_hosts=None):
            logger.info(
                "auth='password' host=%r username=%r password=%r valid='true'",
                host,
                username,
                password,
            )
            return True
    except Exception:
        pass
    logger.info(
        "auth='password' host=%r username=%r password=%r valid='false'",
        host,
        username,
        password,
    )
    return False


class SwitcherooServer(LoggingServer):
    """
    A credential logging and replaying SSH Server.
    """

    @classmethod
    async def check_credentials(cls, host, username, password):
        """
        Try to authenticate with the passed credentials.

        :param username:
        :param password:
        :return: bool indicating validity of the credentials
        :rtype: bool
        """

        return await _check_credentials(host, username, password)

    async def brute(self):
        credentials = Config.load_credentials()
        for username, password in credentials:
            if await self.check_credentials(self.host, username, password):
                break

    async def replay(self, username, password):
        """
        Use the attacker's credentials against himself.
        """
        if await self.check_credentials(self.host, username, password):
            return False

        if Config.CREDENTIALS is not None:
            await self.brute()
        return False

    def validate_password(self, username, password):
        return asyncio.wait_for(self.replay(username, password), timeout=4.0)

