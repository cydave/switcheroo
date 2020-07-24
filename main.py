import argparse
import asyncio
import sys

import asyncssh

from switcheroo.log import setup_logging
from switcheroo.config import Config


logger, listener = setup_logging()


async def start_server():
    logger.info(f"switcheroo listening on %s:%d", Config.HOST, Config.PORT)
    await asyncssh.create_server(
        server_factory=Config.get_server_class(),
        host=Config.HOST,
        port=Config.PORT,
        server_host_keys=Config.HOST_KEYS,
        server_version=Config.BANNER,
    )


def main():
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(start_server())
        loop.run_forever()
    except (OSError, asyncssh.Error) as exc:
        sys.exit("Error starting server: " + str(exc))
    except KeyboardInterrupt:
        pass

    listener.stop()


if __name__ == "__main__":
    main()
