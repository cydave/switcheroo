import argparse
import asyncio
import logging
import sys

import asyncssh

from switcheroo.server import SSHServer


logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger("switcheroo")
hdlr = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)


async def start_server(args):
    logger.info(f"Listening on {args.host}:{args.port}")
    await asyncssh.create_server(
        server_factory=SSHServer,
        host=args.host,
        port=args.port,
        server_host_keys=["/home/me/Documents/code/switcheroo/keys/ssh_host_dsa_key", "/home/me/Documents/code/switcheroo/keys/ssh_host_rsa_key"],
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
