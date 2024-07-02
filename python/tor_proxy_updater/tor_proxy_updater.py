#!/usr/bin/env python3.11
# pylint: disable=multiple-statements
# pylint: disable=line-too-long
# pylint: disable=invalid-name

import asyncio
import logging
import os
from pathlib import Path
from time import sleep

from pyrogram import Client
import nest_asyncio

from config import CONFIG


logging.basicConfig(format="%(asctime)s :: %(levelname)s :: %(message)s", level=logging.INFO, datefmt="%H:%M:%S")


def write_bridges_to_cfg(bridges, cfg_path):
    """
    write bridges to given config file
    """
    logging.info("Writing new proxies")
    if os.path.exists(cfg_path): os.remove(cfg_path)
    cfg_path = open(file=cfg_path, mode='w', encoding='utf-8')
    for bridge in bridges: cfg_path.write(f"Bridge {bridge}\n")
    cfg_path.close()


async def get_bridges_bot():
    logging.info('Grab proxies from telegram bot "GetBridgesBot"')

    bridges = []

    async with Client("my_account", CONFIG["app_config"]["api_id"], CONFIG["app_config"]["api_hash"]) as app:
        await app.send_message("GetBridgesBot", "/bridges")

        sleep(5.31)  # wait for bot response

        async for message in app.get_chat_history(chat_id="GetBridgesBot", limit=5):
            for line in message.text.splitlines():
                line = line.replace("```", "")
                if line.startswith("obfs4") is False: continue
                bridges.append(line)

    write_bridges_to_cfg(bridges, '/etc/tor/conf.d/12bridges.conf')


async def tor_bridges():
    logging.info('Grab proxies from telegram channel "tor_bridges"')

    bridges = []

    async with Client("my_account", CONFIG["app_config"]["api_id"], CONFIG["app_config"]["api_hash"]) as app:
        async for message in app.get_chat_history(chat_id="tor_bridges", limit=5):
            for line in message.text.splitlines():
                line = line.replace("```", "")
                if line.startswith("obfs4") is False: continue
                bridges.append(line)

    write_bridges_to_cfg(bridges, '/etc/tor/conf.d/13bridges.conf')


async def main():
    os.chdir(Path(__file__).parent)

    await get_bridges_bot()
    sleep(5.31)
    await tor_bridges()

    logging.info("Restarting TOR daemon")
    os.system("service tor restart")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    nest_asyncio.apply(loop)
    loop.run_until_complete(main())
