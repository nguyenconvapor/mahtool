import asyncio
import random
import ssl
import json
import time
import uuid
import requests
import backoff
from loguru import logger
from websockets_proxy import Proxy, proxy_connect  # For SOCKS proxies
from aiohttp import ClientSession, TCPConnector  # For HTTP/HTTPS proxies
from fake_useragent import UserAgent
from datetime import datetime, timezone

# List to keep track of active proxies
active_proxies = set()

async def connect_to_wss(proxy_url, user_id):
    user_agent = UserAgent(os=['windows', 'macos', 'linux'], browsers='chrome')
    random_user_agent = user_agent.random
    device_id = str(uuid.uuid3(uuid.NAMESPACE_DNS, proxy_url))

    # Add the proxy to active proxies set
    active_proxies.add(proxy_url)
    logger.info(f"Using proxy: {proxy_url}, device_id: {device_id}, Active proxies: {len(active_proxies)}")

    urilist = ["wss://proxy2.wynd.network:4444/", "wss://proxy2.wynd.network:4650/", "wss://proxy2.wynd.network:443/"]
    server_hostname = "proxy2.wynd.network"
    custom_headers = {"User-Agent": random_user_agent}
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    @backoff.on_exception(backoff.expo, Exception, max_tries=3)
    async def send_websocket_message(websocket, message): #websocket as argument
        await websocket.send(json.dumps(message))

    async def send_ping(websocket):
        while True:
            send_message = {"id": str(uuid.uuid4()), "version": "1.0.0", "action": "PING", "data": {}}
            logger.debug(f"Sending PING: {send_message}")
            await send_websocket_message(websocket, send_message) # Use new function
            await asyncio.sleep(5)

    while True:
        try:
            if proxy_url.startswith("socks"):  # SOCKS proxy
                proxy = Proxy.from_url(proxy_url)
                async with proxy_connect(random.choice(urilist), proxy=proxy, ssl=ssl_context, server_hostname=server_hostname, extra_headers=custom_headers) as websocket:
                    logger.info(f"Connected to {random.choice(urilist)} using {proxy_url}")
                    asyncio.create_task(send_ping(websocket))
                    # ... (websocket handling code remains the same)
                    async for response in websocket:
                        # ... (rest of message handling as before)


            elif proxy_url.startswith("http"):  # HTTP/HTTPS proxy
                async with ClientSession(connector=TCPConnector(ssl=False)) as session:
                    async with session.ws_connect(
                        random.choice(urilist),
                        proxy=proxy_url,
                        ssl=ssl_context,
                        headers=custom_headers
                    ) as websocket:
                         logger.info(f"Connected to {random.choice(urilist)} using {proxy_url}")
                         asyncio.create_task(send_ping(websocket))
                         async for response in websocket:
                            # ... (rest of message handling as before)

            else:
                logger.error(f"Unsupported proxy type: {proxy_url}")
                return

        except Exception as e:
            logger.error(f"Error with proxy {proxy_url}: {e}")
            await asyncio.sleep(random.uniform(1, 5))

def remove_proxy(proxy):
    if proxy in active_proxies:
        active_proxies.remove(proxy)
        logger.info(f"Proxy {proxy} removed. Active proxies: {len(active_proxies)}")


async def main():
    _user_id = '2owgypvuaDXDxUN3gDdVcCwbxYj' # Replace with your user ID
    try:
        r = requests.get("https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=protocolipport&format=text", stream=True) # Replace with your proxy list URL
        r.raise_for_status()
        with open('auto_proxies.txt', 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): # Corrected iter_content usage
                f.write(chunk)

        with open('auto_proxies.txt', 'r') as file:
           auto_proxy_list = [proxy.strip() for proxy in file if proxy.strip()]
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching proxies: {e}")
        return


    tasks = [asyncio.ensure_future(connect_to_wss(i, _user_id)) for i in auto_proxy_list]
    await asyncio.gather(*tasks)




if __name__ == '__main__':
    logger.add(lambda msg: print(msg, end='')) # print to console
    asyncio.run(main())
