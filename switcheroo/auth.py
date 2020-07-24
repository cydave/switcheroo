import asyncio
import logging

import asyncssh

from switcheroo import util

logger = logging.getLogger("switcheroo")


class Auth:
    @classmethod
    def validate_password(cls, host, port, username, password):
        raise NotImplementedError

    @classmethod
    def validate_public_key(cls, host, port, public_key):
        raise NotImplementedError


class LoggingAuth(Auth):
    """
    Credential logging auth handler.
    """

    @classmethod
    def validate_password(cls, host, port, username, password):
        logger.info("auth='password' host=%r username=%r password=%r", f"{host}:{port}", username, password)
        return False

    @classmethod
    def validate_public_key(cls, host, port, public_key):
        md5_fingerprint = util.public_key_to_md5(public_key)
        sha_fingerprint = util.public_key_to_sha(public_key)
        logger.info("auth='pubkey' host=%r md5=%r sha=%r", f"{host}:{port}", md5_fingerprint, sha_fingerprint)
        return False


class SwitcherooAuth(LoggingAuth):
    """
    Credential logging and replaying auth handler.
    """

    @classmethod
    async def switcheroo(cls, host, port, username, password):
        """
        Use the attacker's credentials against himself.

        :param username:
        :param password:
        :return:
        """
        try:
            async with asyncssh.connect(host, username=username, password=password, known_hosts=None):
                logger.info("auth='password' host=%r username=%r password=%r valid=true", f"{host}:{port}", username, password)
                return False
        except Exception:
            logger.info("auth='password' host=%r username=%r password=%r valid=false", f"{host}:{port}", username, password)
        return False

    @classmethod
    def validate_password(cls, host, port, username, password):
        return asyncio.wait_for(cls.switcheroo(host, port, username, password), timeout=3.0)
