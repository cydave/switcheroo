import argparse
import asyncio
import sys

import asyncssh

from switcheroo.log import setup_logging
from switcheroo.config import Config


logger, listener = setup_logging()


async def start_server(args):
    logger.info(f"switcheroo listening on %s:%d", args.host, args.port)
    await asyncssh.create_server(
        server_factory=Config.get_server_class(),
        host=Config.HOST,
        port=Config.PORT,
        server_host_keys=Config.HOST_KEYS,
        server_version=Config.BANNER,
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
    version = ap.add_argument(
        "--server-version", required=False, default="SSH-2.0-OpenSSH_7.4"
    )
    args = ap.parse_args()
    main(args)
    listener.stop()
