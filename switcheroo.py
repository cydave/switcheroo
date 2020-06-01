import argparse
import traceback
import sys
import logging
from datetime import datetime, timezone

import asyncio
import asyncssh


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
hdlr = logging.StreamHandler(stream=sys.stdout)
hdlr.setFormatter(logging.Formatter(fmt="%(message)s"))
logger.addHandler(hdlr)
hdlr = logging.FileHandler("turntables.log", mode="a")
logger.addHandler(hdlr)


def log(message):
    dt = datetime.now(timezone.utc).astimezone().isoformat()
    logger.info(f"{dt} {message}")


class Switcheroo(asyncssh.SSHServer):
    def connection_made(self, con):
        self.con = con
        self.host, self.port = self.get_addr(con)

    @staticmethod
    def get_addr(con):
        host, port = con.get_extra_info("peername")
        return str(host), port

    def begin_auth(self, username):
        return True

    def public_key_auth_supported(self):
        return True

    def password_auth_supported(self):
        return True

    def log(self, message):
        log(f"addr={self.host}:{self.port} {message}")

    async def _check_creds(self, username, password):
        async def _check_inner():
            try:
                async with asyncssh.connect(self.host, username=username, password=password) as con:
                    self.log(f"username={username} password={password!r} valid=true")
            except Exception:
                self.log(f"username={username} password={password!r} valid=false")

        try:
            await asyncio.wait_for(_check_inner(), timeout=1.0)
        except Exception:
            pass
        return False

    def validate_password(self, username, password):
        return asyncio.wait_for(self._check_creds(username, password), timeout=3.0)

    def validate_public_key(self, username, key):
        md5_fp = key.get_fingerprint("md5")[4:]
        sha_fp = key.get_fingerprint("sha256")[7:]
        self.log(f"username={username} md5={md5_fp} sha256={sha_fp} valid=false")
        return False


async def start_server(args):
    log(f"Listening on {args.host}:{args.port}")
    await asyncssh.create_server(
        Switcheroo,
        args.host,
        args.port,
        server_host_keys=["keys/ssh_host_dsa_key", "keys/ssh_host_rsa_key"],
        process_factory=lambda con: con.exit(1),
        server_version=args.server_version,
    )


def main(args):
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(start_server(args))
    except (OSError, asyncssh.Error) as exc:
        sys.exit("Error starting server: " + str(exc))

    loop.run_forever()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    host = ap.add_argument("-b", "--host", required=False, default="0.0.0.0")
    port = ap.add_argument("-p", "--port", type=int, required=False, default=10022)
    keys = ap.add_argument(
        "-k",
        "--key",
        type=list,
        required=False,
        default=["keys/ssh_host_dsa_key", "keys/ssh_host_rsa_key"],
    )
    version = ap.add_argument(
        "--server-version", required=False, default="SSH-2.0-OpenSSH_7.4"
    )
    args = ap.parse_args()
    main(args)
